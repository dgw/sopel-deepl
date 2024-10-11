"""sopel-deepl

DeepL translation plugin for Sopel IRC bots.
"""
from __future__ import generator_stop

import deepl_api
import requests.exceptions

from sopel import plugin
from sopel.config import types
from sopel.tools import get_logger


LOGGER = get_logger('deepl')


class DeepLSection(types.StaticSection):
    auth_key = types.ValidatedAttribute('auth_key', default=types.NO_DEFAULT)
    """Your DeepL account's Authentication Key."""


def configure(config):
    config.define_section('deepl', DeepLSection, validate=False)
    config.deepl.configure_setting(
        'auth_key',
        "Enter your DeepL account's Authentication Key:",
    )


def setup(bot):
    bot.config.define_section('deepl', DeepLSection)

    bot.memory['deepl_instance'] = deepl_api.DeepL(bot.config.deepl.auth_key)


@plugin.commands('deepl')
@plugin.output_prefix('[DeepL] ')
@plugin.rate(30)
def deepl_command(bot, trigger):
    """Translate text using DeepL."""
    text = trigger.group(2)
    if text is None or not text.strip():
        bot.reply("What did you want me to translate?")
        return plugin.NOLIMIT

    try:
        translations = bot.memory['deepl_instance'].translate(
            texts=[text],
            target_language='EN-US',
        )
    except deepl_api.exceptions.DeeplAuthorizationError:
        bot.reply(
            "DeepL says my authorization key is invalid. "
            "Please inform {}.".format(bot.config.core.owner))
        return
    except deepl_api.exceptions.DeeplServerError:
        bot.reply(
            "There was an error on the DeepL server side. "
            "Please try again later."
        )
        return
    except deepl_api.exceptions.DeeplDeserializationError:
        bot.reply(
            "Could not decipher the DeepL server's response. "
            "Please inform {}.".format(bot.config.core.owner)
        )
        return
    except deepl_api.exceptions.DeeplBaseError:
        bot.reply(
            "Unknown error talking to DeepL service. "
            "Please wait a while and try again."
        )
        return
    except requests.exceptions.RequestException as exc:
        bot.reply(
            "Something prevented me from talking to the DeepL service. "
            "Please try again later."
        )
        LOGGER.exception(
            'Error while trying to contact DeepL service'
        )
        return

    if not translations:
        bot.reply(
            "DeepL returned empty translations. This is probably a bug. "
            "Please inform {}.".format(bot.config.core.owner)
        )
        LOGGER.debug(
            'Empty translation result. Input was: %s',
            text,
        )

    bot.say('"{}" (from {})'.format(
        translations[0]['text'],
        translations[0]['detected_source_language'],
    ))

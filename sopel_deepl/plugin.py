"""sopel-deepl

DeepL translation plugin for Sopel IRC bots.

Licensed under the Eiffel Forum License 2.

Copyright 2021-2024 dgw, technobabbl.es
"""
from __future__ import annotations

import deepl_api
import requests.exceptions

from sopel import plugin
from sopel.config import types
from sopel.tools import get_logger

from . import util


LOGGER = get_logger('deepl')


class DeepLSection(types.StaticSection):
    auth_key = types.SecretAttribute('auth_key', default=types.NO_DEFAULT)
    """Your DeepL account's Authentication Key."""
    default_target = types.ValidatedAttribute('default_target', default='EN-US')
    """The bot-wide default target language code."""


def configure(config):
    config.define_section('deepl', DeepLSection, validate=False)
    config.deepl.configure_setting(
        'auth_key',
        "Enter your DeepL API Key:",
    )
    config.deepl.configure_setting(
        'default_target',
        'Enter the default target language code:',
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

    target_lang = util.get_preferred_target(
        bot, trigger.nick, trigger.sender
    )

    try:
        translations = bot.memory['deepl_instance'].translate(
            texts=[text],
            target_language=target_lang,
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

    bot.say(
        '"' + translations[0]['text'],
        truncation='…',
        trailing='" ({} 🡒 {})'.format(
            translations[0]['detected_source_language'],
            target_lang,
        ),
    )


@plugin.commands('deeplang')
@plugin.example('.deeplang DE')
def set_user_target(bot, trigger):
    """Set or view your preferred target language for translations."""
    if not (target := trigger.group(3)):
        if setting := bot.db.get_nick_value(trigger.nick, util.TARGET_SETTING_NAME, None):
            msg = (
                "Your preferred target language is currently set to {}. "
                "(To clear this setting, use `{}deeplang -`.)"
                .format(setting, bot.settings.core.help_prefix)
            )
        else:
            msg = "What language code do you want to use?"

        bot.reply(msg)
        return plugin.NOLIMIT

    util.set_preferred_target(bot, trigger.nick, target)
    action = ("cleared" if target == "-" else "set to " + target)
    bot.reply("Your preferred target language is now {}.".format(action))


@plugin.commands('deepclang')
@plugin.example('.deepclang DE')
@plugin.require_privilege(  # require_chanmsg() is implied as of Sopel 8.0
    plugin.OP,
    "You must be a channel operator to change this setting.")
def set_channel_target(bot, trigger):
    """Set or view the channel's preferred target language for translations."""
    if not (target := trigger.group(3)):
        if setting := bot.db.get_channel_value(trigger.sender, util.TARGET_SETTING_NAME, None):
            msg = (
                "The preferred target language for this channel is currently set to {}. "
                "(To clear this setting, use `{}deepclang -`.)"
                .format(setting, bot.settings.core.help_prefix)
            )
        else:
            msg = "What language code do you want to use?"

        bot.reply(msg)
        return plugin.NOLIMIT

    util.set_preferred_target(bot, trigger.sender, target)
    action = ("cleared" if target == "-" else "set to " + target)
    bot.reply("The preferred target language for this channel is now {}.".format(action))

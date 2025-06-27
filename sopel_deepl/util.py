"""sopel-deepl utility submodule

Part of sopel-deepl.

Licensed under the Eiffel Forum License 2.

Copyright 2024 dgw, technobabbl.es
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sopel import SopelWrapper
    from sopel.tools.identifiers import Identifier


TARGET_SETTING_NAME = 'deepl_target'


def get_preferred_target(
    bot: SopelWrapper,
    nick: Identifier | None,
    context: Identifier | None,
) -> str:
    """Get the preferred target language for a user in a given context."""
    if nick and nick.is_nick() and (
        target := bot.db.get_nick_value(nick, TARGET_SETTING_NAME, None)
    ):
        return target
    elif context and not context.is_nick() and (
        target := bot.db.get_channel_value(context, TARGET_SETTING_NAME, None)
    ):
        return target
    else:
        return bot.settings.deepl.default_target


def set_preferred_target(
    bot: SopelWrapper,
    context: Identifier,
    target: str,
) -> None:
    """Set the preferred ``target`` language for a ``context`` (user or channel)."""
    if context.is_nick():
        if target == '-':
            bot.db.delete_nick_value(context, TARGET_SETTING_NAME)
        else:
            bot.db.set_nick_value(context, TARGET_SETTING_NAME, target)
    else:
        if target == '-':
            bot.db.delete_channel_value(context, TARGET_SETTING_NAME)
        else:
            bot.db.set_channel_value(context, TARGET_SETTING_NAME, target)

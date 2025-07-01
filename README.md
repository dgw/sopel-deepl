# sopel-deepl

DeepL translation plugin for Sopel IRC bots.

## Installation

This plugin is released on PyPI, so it's easy to install using `pip`:

    pip install sopel-deepl

Sopel loads all available plugins by default. If you have changed your bot to
the ["enabled only" mode][enable-only-plugins], edit your config file to enable
the `deepl` plugin or run `sopel-plugins enable deepl` in your terminal.

[enable-only-plugins]: https://sopel.chat/docs/run/plugin#enable-only-plugins

## Usage

```
.deepl [text to translate]

# Totally-not-contrived example
<dgw> .deepl Dormez-vous?
<Sopel> [DeepL] "Are you asleep?" (FR 🡒 EN-US)
```

The target language can be configured globally, with overrides at the channel
and user levels via IRC commands; see below.

### Configuring global settings

The easiest way to configure this plugin is using Sopel's built-in wizard: In
your terminal, run `sopel-plugins configure deepl` and follow the prompts.

These settings are also configurable by editing the `[deepl]` section of your
bot's config file manually, if you choose.

```ini
[deepl]
auth_key = your_DeepL_API_key  # required
default_target = FR  # optional; defaults to EN-US
```

Refer to [DeepL's list of supported target languages][target-langs] when
choosing a value for `default_target`.

### Configuring user settings

```
# set to French
.deeplang FR

# clear user preference
.deeplang -
```

Users can set their preferred target language for translations using the
`.deeplang` command. See [DeepL's supported target languages][target-langs].

The special value `-` clears this setting.

### Configuring channel settings

```
# set to French
.deepclang FR

# clear channel setting
.deepclang -
```

Channel operators and higher can set a channel's default target language,
overriding the bot's global default, using the `.deepclang` command. See
[DeepL's list of supported target languages][target-langs].

The special value `-` clears this setting.

## Limitations

In some cases, it might be useful to pass a source-language hint along with the
input text. DeepL's language detection is fairly good when given well-formed
source material, but it can make wild incorrect guesses on "wrong" usage. (For
example, passing the earlier `Dormez-vous?` example without the hyphen yielded a
guessed source language of Hungarian instead of French during testing.)

`sopel-deepl` doesn't support such a feature yet, but it's on the radar.


[target-langs]: https://developers.deepl.com/docs/getting-started/supported-languages#translation-target-languages

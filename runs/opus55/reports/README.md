# Agent session reports

100 sessions, total cost $39.66. Each page shows the agent's final report and run statistics.
The runs recorded only the final report per session (`claude -p --output-format json`), not the turn-by-turn
conversation. Checks and Rector figures come from scoring on a pristine copy of the harness.

| File | Checks | Original | Rector found | Resolved | Remaining rules | Turns | Seconds | Cost | Denials |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| [001_getid3.lib](001_getid3.lib.md) | 6/6 | 0/6 | 12 | 12 |  | 21 | 312 | $1.56 | 2 |
| [002_module.audio-video.asf](002_module.audio-video.asf.md) | 5/5 | 0/5 | 12 | 10 | StringifyDefineRector, SensitiveConstantNameRector | 28 | 238 | $0.87 | 3 |
| [003_wp-db](003_wp-db.md) | 7/7 | 7/7 | 12 | 11 | ClassPropertyAssignToConstructorPromotionRector | 25 | 116 | $0.45 | 1 |
| [004_class-IXR](004_class-IXR.md) | 8/8 | 2/8 | 9 | 9 |  | 30 | 259 | $1.20 | 1 |
| [005_class-snoopy](005_class-snoopy.md) | 6/6 | 3/6 | 5 | 4 | AssignArrayToStringRector | 14 | 229 | $0.99 | 1 |
| [006_widgets](006_widgets.md) | 5/5 | 5/5 | 9 | 6 | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector, FirstClassCallableRector | 20 | 92 | $0.39 | 1 |
| [007_class-wp](007_class-wp.md) | 7/7 | 3/7 | 9 | 7 | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector | 43 | 189 | $0.81 | 2 |
| [008_wp-login](008_wp-login.md) | 7/7 | 7/7 | 8 | 7 | NullToStrictStringFuncCallArgRector | 24 | 97 | $0.40 | 1 |
| [009_getid3](009_getid3.md) | 0/6 | 0/6 | 8 | 7 | NullToStrictStringFuncCallArgRector | 59 | 232 | $1.15 | 3 |
| [010_class-wp-theme](010_class-wp-theme.md) | 7/7 | 7/7 | 7 | 5 | ClassPropertyAssignToConstructorPromotionRector, ChangeSwitchToMatchRector | 17 | 89 | $0.54 | 1 |
| [011_translations](011_translations.md) | 6/6 | 4/6 | 8 | 8 |  | 10 | 86 | $0.33 | 1 |
| [012_module.audio-video.riff](012_module.audio-video.riff.md) | 6/6 | 6/6 | 9 | 9 |  | 40 | 218 | $0.82 | 4 |
| [013_file](013_file.md) | 10/10 | 10/10 | 8 | 8 |  | 38 | 131 | $0.66 | 1 |
| [014_module.tag.id3v2](014_module.tag.id3v2.md) | 6/6 | 0/6 | 9 | 8 | ChangeSwitchToMatchRector | 34 | 359 | $1.12 | 5 |
| [015_Diff](015_Diff.md) | 7/7 | 1/7 | 6 | 5 | Php4ConstructorRector | 8 | 100 | $0.42 | 1 |
| [016_module.audio.ac3](016_module.audio.ac3.md) | 6/6 | 0/6 | 7 | 7 |  | 8 | 135 | $0.62 | 1 |
| [017_press-this](017_press-this.md) | 5/5 | 5/5 | 7 | 7 |  | 26 | 102 | $0.41 | 2 |
| [018_streams](018_streams.md) | 8/8 | 2/8 | 6 | 6 |  | 9 | 96 | $0.38 | 1 |
| [019_atomlib](019_atomlib.md) | 5/5 | 1/5 | 8 | 8 |  | 14 | 221 | $0.58 | 2 |
| [020_class-ftp](020_class-ftp.md) | 8/8 | 0/8 | 7 | 7 | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector | 10 | 244 | $1.01 | 1 |
| [021_class-pop3](021_class-pop3.md) | 10/10 | 0/10 | 7 | 7 |  | 12 | 226 | $0.63 | 1 |
| [022_class-wp-customize-setting](022_class-wp-customize-setting.md) | 10/10 | 10/10 | 6 | 3 | ClassPropertyAssignToConstructorPromotionRector, ChangeSwitchToMatchRector, FirstClassCallableRector | 15 | 156 | $0.39 | 1 |
| [023_module.tag.id3v1](023_module.tag.id3v1.md) | 10/10 | 0/10 | 6 | 6 |  | 19 | 186 | $0.48 | 1 |
| [024_edit-form-advanced](024_edit-form-advanced.md) | 3/3 | 3/3 | 6 | 6 |  | 8 | 68 | $0.22 | 1 |
| [025_widgets](025_widgets.md) | 3/3 | 3/3 | 6 | 6 |  | 7 | 116 | $0.46 | 1 |
| [026_Source](026_Source.md) | 4/4 | 4/4 | 6 | 5 | ClassPropertyAssignToConstructorPromotionRector | 21 | 98 | $0.30 | 1 |
| [027_upload](027_upload.md) | 4/4 | 4/4 | 6 | 6 |  | 8 | 144 | $0.41 | 1 |
| [028_themes](028_themes.md) | 4/4 | 4/4 | 6 | 5 | NullToStrictStringFuncCallArgRector | 17 | 131 | $0.30 | 1 |
| [029_module.audio.ogg](029_module.audio.ogg.md) | 4/4 | 4/4 | 6 | 6 |  | 25 | 129 | $0.53 | 2 |
| [030_class-json](030_class-json.md) | 7/7 | 0/7 | 6 | 6 | Php4ConstructorRector, BinaryOpBetweenNumberAndStringRector | 25 | 331 | $1.15 | 1 |
| [031_class-wp-plugins-list-table](031_class-wp-plugins-list-table.md) | 4/4 | 4/4 | 6 | 6 |  | 26 | 167 | $0.46 | 2 |
| [032_class-wp-comments-list-table](032_class-wp-comments-list-table.md) | 5/5 | 5/5 | 5 | 5 |  | 34 | 170 | $0.58 | 2 |
| [033_ms-settings](033_ms-settings.md) | 5/5 | 5/5 | 6 | 6 |  | 16 | 71 | $0.26 | 1 |
| [034_inline](034_inline.md) | 5/5 | 5/5 | 6 | 6 |  | 7 | 70 | $0.25 | 1 |
| [035_wp-trackback](035_wp-trackback.md) | 7/7 | 7/7 | 5 | 5 |  | 11 | 57 | $0.20 | 1 |
| [036_module.tag.apetag](036_module.tag.apetag.md) | 6/6 | 6/6 | 5 | 5 |  | 7 | 119 | $0.54 | 1 |
| [037_class-wp-ms-sites-list-table](037_class-wp-ms-sites-list-table.md) | 6/6 | 6/6 | 5 | 5 |  | 22 | 63 | $0.33 | 1 |
| [038_class.wp-styles](038_class.wp-styles.md) | 6/6 | 6/6 | 5 | 5 |  | 12 | 52 | $0.20 | 1 |
| [039_class-wp-upgrader-skins](039_class-wp-upgrader-skins.md) | 7/7 | 7/7 | 5 | 5 |  | 22 | 105 | $0.52 | 2 |
| [040_class-wp-media-list-table](040_class-wp-media-list-table.md) | 7/7 | 7/7 | 5 | 4 | NullToStrictStringFuncCallArgRector | 36 | 122 | $0.44 | 1 |
| [041_module.tag.lyrics3](041_module.tag.lyrics3.md) | 5/5 | 5/5 | 5 | 5 |  | 14 | 60 | $0.29 | 1 |
| [042_image-edit](042_image-edit.md) | 4/4 | 4/4 | 5 | 3 | ChangeSwitchToMatchRector, NullToStrictStringFuncCallArgRector | 11 | 67 | $0.25 | 1 |
| [043_image](043_image.md) | 4/4 | 4/4 | 5 | 5 |  | 28 | 96 | $0.44 | 1 |
| [044_class-wp-image-editor](044_class-wp-image-editor.md) | 5/5 | 5/5 | 5 | 4 | ClassPropertyAssignToConstructorPromotionRector | 14 | 67 | $0.26 | 1 |
| [045_Locator](045_Locator.md) | 5/5 | 5/5 | 4 | 3 | ClassPropertyAssignToConstructorPromotionRector | 8 | 99 | $0.41 | 1 |
| [046_module.audio-video.flv](046_module.audio-video.flv.md) | 5/5 | 5/5 | 5 | 3 | Php4ConstructorRector, ClassPropertyAssignToConstructorPromotionRector | 30 | 172 | $0.80 | 1 |
| [047_update-core](047_update-core.md) | 5/5 | 5/5 | 5 | 5 |  | 22 | 66 | $0.29 | 1 |
| [048_about](048_about.md) | 5/5 | 5/5 | 5 | 5 |  | 10 | 46 | $0.21 | 1 |
| [049_Parser](049_Parser.md) | 5/5 | 5/5 | 5 | 5 |  | 22 | 90 | $0.43 | 1 |
| [050_class-oembed](050_class-oembed.md) | 5/5 | 5/5 | 5 | 5 |  | 24 | 107 | $0.51 | 1 |
| [051_ms-deprecated](051_ms-deprecated.md) | 5/5 | 5/5 | 4 | 4 |  | 12 | 62 | $0.27 | 1 |
| [052_class-wp-ms-themes-list-table](052_class-wp-ms-themes-list-table.md) | 5/5 | 5/5 | 5 | 5 |  | 10 | 105 | $0.47 | 2 |
| [053_class-wp-themes-list-table](053_class-wp-themes-list-table.md) | 5/5 | 5/5 | 5 | 5 |  | 17 | 65 | $0.31 | 2 |
| [054_nav-menu](054_nav-menu.md) | 5/5 | 5/5 | 4 | 4 |  | 19 | 91 | $0.30 | 1 |
| [055_rss](055_rss.md) | 5/5 | 5/5 | 5 | 5 |  | 41 | 178 | $0.72 | 1 |
| [056_class.akismet](056_class.akismet.md) | 5/5 | 5/5 | 4 | 4 |  | 17 | 71 | $0.29 | 1 |
| [057_class-wp-customize-manager](057_class-wp-customize-manager.md) | 5/5 | 5/5 | 4 | 3 | FirstClassCallableRector | 10 | 57 | $0.22 | 1 |
| [058_session](058_session.md) | 5/5 | 5/5 | 4 | 4 |  | 15 | 42 | $0.22 | 1 |
| [059_credits](059_credits.md) | 5/5 | 5/5 | 5 | 5 |  | 8 | 40 | $0.17 | 1 |
| [060_themes](060_themes.md) | 5/5 | 5/5 | 5 | 5 |  | 22 | 66 | $0.36 | 1 |
| [061_class.wp-scripts](061_class.wp-scripts.md) | 5/5 | 5/5 | 5 | 4 | FirstClassCallableRector | 13 | 56 | $0.21 | 1 |
| [062_string](062_string.md) | 4/4 | 4/4 | 5 | 5 |  | 9 | 63 | $0.24 | 1 |
| [063_module.audio.dts](063_module.audio.dts.md) | 5/5 | 5/5 | 4 | 3 | ChangeSwitchToMatchRector | 12 | 55 | $0.22 | 1 |
| [064_wp-diff](064_wp-diff.md) | 5/5 | 5/5 | 5 | 5 |  | 25 | 90 | $0.40 | 1 |
| [065_class-wp-image-editor-imagick](065_class-wp-image-editor-imagick.md) | 5/5 | 5/5 | 5 | 4 | FirstClassCallableRector | 19 | 74 | $0.34 | 1 |
| [066_class.wp-dependencies](066_class.wp-dependencies.md) | 5/5 | 5/5 | 5 | 4 | RemoveExtraParametersRector | 11 | 47 | $0.22 | 1 |
| [067_user](067_user.md) | 5/5 | 5/5 | 4 | 4 |  | 21 | 72 | $0.35 | 1 |
| [068_revision](068_revision.md) | 5/5 | 5/5 | 4 | 4 |  | 26 | 90 | $0.42 | 2 |
| [069_class-wp-image-editor-gd](069_class-wp-image-editor-gd.md) | 5/5 | 1/5 | 4 | 3 | ChangeSwitchToMatchRector | 24 | 78 | $0.37 | 1 |
| [070_File](070_File.md) | 4/4 | 4/4 | 4 | 3 | ClassPropertyAssignToConstructorPromotionRector | 13 | 51 | $0.23 | 1 |
| [071_plugins](071_plugins.md) | 3/3 | 3/3 | 4 | 4 |  | 24 | 66 | $0.36 | 1 |
| [072_class-wp-users-list-table](072_class-wp-users-list-table.md) | 3/3 | 3/3 | 4 | 3 | NullToStrictStringFuncCallArgRector | 19 | 67 | $0.31 | 1 |
| [073_site-settings](073_site-settings.md) | 10/10 | 10/10 | 4 | 4 |  | 16 | 66 | $0.25 | 1 |
| [074_site-themes](074_site-themes.md) | 14/14 | 14/14 | 3 | 3 |  | 6 | 80 | $0.27 | 1 |
| [075_my-sites](075_my-sites.md) | 11/11 | 11/11 | 3 | 3 |  | 9 | 42 | $0.16 | 1 |
| [076_upgrade](076_upgrade.md) | 10/10 | 10/10 | 3 | 3 |  | 10 | 52 | $0.17 | 1 |
| [077_post-thumbnail-template](077_post-thumbnail-template.md) | 11/11 | 11/11 | 3 | 3 |  | 7 | 49 | $0.14 | 1 |
| [078_media](078_media.md) | 12/12 | 12/12 | 3 | 3 |  | 14 | 62 | $0.19 | 1 |
| [079_load-styles](079_load-styles.md) | 10/10 | 10/10 | 3 | 3 |  | 13 | 93 | $0.21 | 1 |
| [080_site-info](080_site-info.md) | 9/9 | 9/9 | 3 | 3 |  | 17 | 90 | $0.24 | 1 |
| [081_site-new](081_site-new.md) | 9/9 | 9/9 | 3 | 2 | NullToStrictStringFuncCallArgRector | 16 | 73 | $0.24 | 1 |
| [082_import](082_import.md) | 8/8 | 8/8 | 3 | 3 |  | 11 | 42 | $0.17 | 1 |
| [083_shell](083_shell.md) | 7/7 | 7/7 | 3 | 3 |  | 11 | 60 | $0.18 | 1 |
| [084_class-wp-ajax-response](084_class-wp-ajax-response.md) | 9/9 | 9/9 | 3 | 3 |  | 9 | 58 | $0.17 | 1 |
| [085_async-upload](085_async-upload.md) | 9/9 | 9/9 | 3 | 3 |  | 13 | 66 | $0.20 | 1 |
| [086_user-new](086_user-new.md) | 8/8 | 8/8 | 3 | 3 |  | 12 | 50 | $0.17 | 1 |
| [087_Restriction](087_Restriction.md) | 7/7 | 7/7 | 3 | 3 |  | 8 | 66 | $0.21 | 1 |
| [088_Credit](088_Credit.md) | 7/7 | 7/7 | 3 | 3 |  | 6 | 46 | $0.16 | 1 |
| [089_Category](089_Category.md) | 7/7 | 7/7 | 3 | 3 |  | 9 | 70 | $0.20 | 1 |
| [090_Author](090_Author.md) | 6/6 | 6/6 | 3 | 3 |  | 14 | 55 | $0.21 | 2 |
| [091_Rating](091_Rating.md) | 6/6 | 6/6 | 3 | 3 |  | 6 | 37 | $0.14 | 1 |
| [092_Copyright](092_Copyright.md) | 6/6 | 6/6 | 3 | 3 |  | 8 | 45 | $0.17 | 1 |
| [093_vars](093_vars.md) | 6/6 | 6/6 | 3 | 3 |  | 7 | 105 | $0.30 | 1 |
| [094_class.akismet-widget](094_class.akismet-widget.md) | 9/9 | 9/9 | 3 | 2 | FirstClassCallableRector | 13 | 53 | $0.17 | 1 |
| [095_class-wp-http-ixr-client](095_class-wp-http-ixr-client.md) | 10/10 | 10/10 | 3 | 3 |  | 7 | 41 | $0.15 | 1 |
| [096_class-ftp-pure](096_class-ftp-pure.md) | 6/6 | 6/6 | 3 | 2 | Php4ConstructorRector | 15 | 72 | $0.29 | 1 |
| [097_class-wp-customize-section](097_class-wp-customize-section.md) | 6/6 | 6/6 | 2 | 1 | ClassPropertyAssignToConstructorPromotionRector | 9 | 41 | $0.19 | 1 |
| [098_wp-load](098_wp-load.md) | 6/6 | 6/6 | 3 | 3 |  | 8 | 46 | $0.14 | 1 |
| [099_ms-files](099_ms-files.md) | 6/6 | 6/6 | 3 | 3 |  | 10 | 60 | $0.17 | 1 |
| [100_wp-links-opml](100_wp-links-opml.md) | 5/5 | 5/5 | 3 | 3 |  | 12 | 64 | $0.18 | 1 |

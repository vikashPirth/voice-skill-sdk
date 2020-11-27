# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

* Actually send null lists for `nestedIn`/`overlapsWith` properties.
* Currently, `startIndex` and `endIndex` are omitted when extracting entity values for freetext, see [SHCC-2587](https://gard.telekom.de/gard/browse/SHCC-2587). This behaviour will be corrected in a future version.

## [1.1] 2020-10-30
* Send half-open date time ranges as entity values, for example `2018-01-01/` (note the trailing slash). 
* Such entity values have been dropped before, see [SHCC-2318](https://gard.telekom.de/gard/browse/SHCC-2318) and linked tickets.

## [1.0] 2020-10-30
* Initial release indicating start of [SPI versioning](https://gard.telekom.de/gard/browse/SVH-2071) support
* DTOs were cleaned up using lombok
* `spiVersion` added to `InvokeSkillRequestDto` 

## [0.9.2] - [0.9.5] 2020-10-06
* Releases due to CI pipeline issues and preparing Skill SPI versioning 

## [0.9.1] 2020-05-15
* [SHCC-2059](https://gard.telekom.de/gard/browse/SHCC-2059)
Add target device id field into the ResultDto. 

## [0.8.4] 2019-07-17
* [SHCC-1289](https://gard.telekom.de/gard/browse/SHCC-1289)
Reintroduce attribute map as map of objects.

## [0.8.3] 2019-06-28
### Changed
* [SHCC-1289](https://gard.telekom.de/gard/browse/SHCC-1289)
Remove attribute map as map of objects.

## [0.8.2] 2019-06-25
### Note
As implementing SHCC-1289 led to further discussions this version should be
considered broken. User version 0.8.3 instead.
### Changed
* [SHCC-1289](https://gard.telekom.de/gard/browse/SHCC-1289)
Add attribute map as map of objects.

## [0.8.1] 2019-03-05
### Changed
* [SHCC-1012](https://gard.telekom.de/gard/browse/SHCC-1012)
Remove dependency to cvi-dependencies BOM.

## [0.8.0] 2018-12-10
### Changed
* [SHCC-831](https://gard.telekom.de/gard/browse/SHCC-831)
Add support for ASK_FREETEXT skill result type.

## [0.7.7] 2018-10-08
### Changed
* [SHCC-292](https://gard.telekom.de/gard/browse/SHCC-292)
Internal dependency updates.

## [0.7.6] 2018-07-24
### Changed
* [SHCC-503](https://gard.telekom.de/gard/browse/SHCC-503)
Add optional `skillVersion` to `SkillInfoResponseDto`.

## [0.7.5] 2018-06-12
### Changed
* [SHCC-393](https://gard.telekom.de/gard/browse/SHCC-393)
Breaking change: Remove `tokens` from `SkillInfoResponseDto`, because token metadata come from skill manifest in cvi core.
No breaking change: Adding enum `ErrorType` for possible error responses.

## [0.7.4] 2018-06-08
### Changed
* [SHCC-436](https://gard.telekom.de/gard/browse/SHCC-436) 
No breaking changes. Removed tokenId (nullable) from CardDto.

## [0.7.3] 2018-02-06
### Changed
* [SHCC-179](https://gard.telekom.de/gard/browse/SHCC-179) 
No breaking changes. Adding `configuration` JSON Key to the skill context `SkillContextDto` on invocation. 
See the [concept for generic skill configuration](https://gard.telekom.de/gardwiki/display/SH/Generic+skill+configuration) for details.

## [0.7.2] 2017-12-13
### Changed
* [SHCC-60](https://gard.telekom.de/gard/browse/SHCC-60) 
No breaking changes, added swagger annotations to provide more documentation for the enum tokentypes and 
tokenParameterDtos.  

## [0.7.1] 2017-10-12
### Changed
* [SHC-537](https://gard.telekom.de/gard/browse/SHC-537) Modify the representation of a push notification to include only a target device name instead of a device id or a phone id.

## [0.7.0] 2017-10-10
### Changed
* [SHC-789](https://gard.telekom.de/gard/browse/SHC-789) Generalization of the predefined concept names. See [the documentation](https://gard.telekom.de/gardwiki/display/SH/2017-08-31+Mapping+von+Predefined+Concepts)
* [SH-1559](https://gard.telekom.de/gard/browse/SH-1559) Revised `Card` JSON format    

## [0.6.4] - 2017-08-28
### Added
* [SHC-825](https://gard.telekom.de/gard/browse/SHC-825) `supportedLocales` field in `SkillInfoResponseDto`

## [0.6.3] - 2017-08-23
### Added
* [SHC-841](https://gard.telekom.de/gard/browse/SHC-841) `data` field to `CardDto`

## [0.6.2] - 2017-08-21
### Added
* Changelog
* [SHC-798](https://gard.telekom.de/gard/browse/SHC-798) Support for IDM exchanged tokens  

## [0.6.1] - 2017-07-27
## [0.6.0] - 2017-07-12
## [0.5.0] - 2017-05-29

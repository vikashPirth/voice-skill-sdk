#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from skill_sdk import i18n
from skill_sdk.responses import (
    Card,
    CardAction,
)
from skill_sdk.responses.card import (
    ListItem,
    ListSection,
    CARD_VERSION,
    GENERIC_DEFAULT,
)


def test_init():
    sc = Card(title_text="Title", text="Text")
    assert sc.title_text == "Title"
    assert sc.text == "Text"


def test_dict():
    assert Card().dict() == {
        "type": GENERIC_DEFAULT,
        "version": CARD_VERSION,
        "data": {},
    }
    assert Card(title_text="Title", text="Text").dict() == {
        "type": GENERIC_DEFAULT,
        "version": CARD_VERSION,
        "data": {"titleText": "Title", "text": "Text"},
    }


def test_l10n_message():
    d = Card(title_text=i18n.Message("TITLE", param1="param1", param2="param2")).dict()
    assert d["data"] == {"titleText": "TITLE"}


def test_list_sections():
    section = ListSection(
        "Section Title", items=[ListItem("Item 1"), ListItem("Item 2")]
    )

    card = Card(list_sections=[section])
    assert card.dict() == {
        "type": GENERIC_DEFAULT,
        "version": CARD_VERSION,
        "data": {
            "listSections": [
                {
                    "title": "Section Title",
                    "items": [{"itemText": "Item 1"}, {"itemText": "Item 2"}],
                }
            ]
        },
    }
    card = Card(list_sections=[ListSection().with_list_item(ListItem("Lonely item"))])
    assert card.dict()["data"] == {
        "listSections": [
            {
                "items": [{"itemText": "Lonely item"}],
            }
        ]
    }
    card = Card(
        list_sections=[
            ListSection()
            .with_list_item("No longer lonely")
            .with_list_item("Another one")
        ]
    )
    assert card.dict()["data"] == {
        "listSections": [
            {
                "items": [
                    {"itemText": "No longer lonely"},
                    {"itemText": "Another one"},
                ],
            }
        ]
    }


def test_with_action():
    sc = Card().with_action(
        "Call this number", CardAction.INTERNAL_CALL.format(number="1234567890")
    )
    assert sc.dict()["data"] == {
        "listSections": [
            {
                "items": [
                    {
                        "itemText": "Call this number",
                        "itemAction": "internal://deeplink/call/1234567890",
                    }
                ]
            }
        ]
    }

    sc = Card(
        list_sections=[
            ListSection().with_list_item(
                "Open App",
                CardAction.INTERNAL_OPEN_APP.format(
                    aos_package_name="package",
                    ios_url_scheme="urlScheme",
                    ios_app_store_id="appStoreId",
                ),
            )
        ]
    )
    assert sc.dict()["data"] == {
        "listSections": [
            {
                "items": [
                    {
                        "itemText": "Open App",
                        "itemAction": "internal://deeplink/openapp?aos=package&iosScheme=urlScheme&iosAppStoreId=appStoreId",
                    }
                ]
            }
        ]
    }

    sc = Card().with_action("Click this URL", "http://example.com")
    assert sc.dict()["data"] == {
        "listSections": [
            {
                "items": [
                    {"itemText": "Click this URL", "itemAction": "http://example.com"}
                ]
            }
        ]
    }


def test_with_list_section():
    sc = Card().with_list_section("Section Title", items=[ListItem("Item Title")])
    assert sc.dict()["data"]["listSections"] == [
        {
            "title": "Section Title",
            "items": [
                {
                    "itemText": "Item Title",
                }
            ],
        }
    ]

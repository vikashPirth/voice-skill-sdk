#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import unittest

from skill_sdk import i18n
from skill_sdk.responses import (
    Card,
    CardAction,
    card,
)


class TestCard(unittest.TestCase):
    def test_init(self):
        sc = Card(type="DEMOTYPE", title_text="Title", text="Text")
        self.assertEqual(sc.title_text, "Title")
        self.assertEqual(sc.text, "Text")

    def test_dict(self):
        sc = Card("DEMOTYPE")
        self.assertDictEqual(
            sc.dict(), {"type": card.GENERIC_DEFAULT, "version": 1, "data": {}}
        )
        sc = Card("DEMOTYPE", title_text="Title", text="Text")
        self.assertDictEqual(
            sc.dict(),
            {
                "type": card.GENERIC_DEFAULT,
                "version": 1,
                "data": {"titleText": "Title", "text": "Text"},
            },
        )

    def test_l10n_message(self):
        d = Card(
            title_text=i18n.Message("TITLE", param1="param1", param2="param2")
        ).dict()
        self.assertEqual({"titleText": "TITLE"}, d["data"])

    def test_list_sections(self):
        sc = Card(
            list_sections=[
                card.ListSection(
                    "Section Title", [card.ListItem("Item 1"), card.ListItem("Item 2")]
                )
            ]
        ).dict()
        self.assertEqual(
            {
                "type": "GENERIC_DEFAULT",
                "version": 1,
                "data": {
                    "listSections": [
                        {
                            "title": "Section Title",
                            "items": [{"title": "Item 1"}, {"title": "Item 2"}],
                        }
                    ]
                },
            },
            sc,
        )

    def test_with_action(self):
        sc = Card().with_action(
            "Call this number", CardAction.INTERNAL_CALL, number="1234567890"
        )
        self.assertEqual(
            {
                "type": "GENERIC_DEFAULT",
                "version": 1,
                "data": {
                    "action": "internal://deeplink/call/1234567890",
                    "actionText": "Call this number",
                },
            },
            sc.dict(),
        )

        sc = sc.with_action(
            "Open App",
            CardAction.INTERNAL_OPEN_APP,
            aos_package_name="package",
            ios_url_scheme="urlScheme",
            ios_app_store_id="appStoreId",
        )
        self.assertEqual(
            {
                "type": "GENERIC_DEFAULT",
                "version": 1,
                "data": {
                    "action": "internal://deeplink/openapp?aos=package&iosScheme=urlScheme&iosAppStoreId=appStoreId",
                    "actionText": "Open App",
                },
            },
            sc.dict(),
        )

        sc = Card().with_action("Click this URL", "http://example.com")
        self.assertEqual(
            {
                "type": "GENERIC_DEFAULT",
                "version": 1,
                "data": {
                    "action": "http://example.com",
                    "actionText": "Click this URL",
                },
            },
            sc.dict(),
        )

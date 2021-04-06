#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Companion app (cApp) cards"""

from enum import Enum
from typing import List, Optional, Text, Union
from skill_sdk.util import CamelModel

# Supported card version
CARD_VERSION = 1

# The only card type available: "GENERIC_DEFAULT"
GENERIC_DEFAULT = "GENERIC_DEFAULT"


class ListItem(CamelModel):
    """
    List item in Card's list sections
    """

    title: Text
    icon_url: Optional[Text] = None

    def __init__(self, title: Text, icon_url: Text = None):
        super().__init__(title=title, icon_url=icon_url)


class ListSection(CamelModel):
    """
    List section in a Card
    """

    title: Text
    items: List[ListItem]

    def __init__(self, title: Text, items: List[ListItem]):
        super().__init__(title=title, items=items)


class CardAction(Text, Enum):
    """
    Card action link can be either one of internal "deep links" (enumerated below)
        or any external "http/https" URL

    """

    # Present skill details view
    INTERNAL_SKILLS = "internal://deeplink/skills"

    # Present overview of all devices
    INTERNAL_OVERVIEW = "internal://deeplink/speakeroverview"

    # Present device details page of the one device that was spoken into to generate this card
    INTERNAL_DETAILS = "internal://deeplink/speakerdetails"

    # Present feedback page in the app
    INTERNAL_FEEDBACK = "internal://deeplink/feedback"

    # Link to the news section of the app
    INTERNAL_NEWS = "internal://deeplink/news"

    # Present full text of the response in an overlay
    INTERNAL_RESPONSE_TEXT = "internal://showResponseText"

    # Initiate a call to the given phone number.
    INTERNAL_CALL = "internal://deeplink/call/{number}"

    # Open a specified app or the App Store if the app is not installed
    INTERNAL_OPEN_APP = (
        "internal://deeplink/openapp?"
        "aos={aos_package_name}&"
        "iosScheme={ios_url_scheme}&"
        "iosAppStoreId={ios_app_store_id}"
    )


class CardData(CamelModel):
    """Companion app card data"""

    # Card title
    title_text: Optional[Text] = None

    # Card subtitle
    type_description: Optional[Text] = None

    # Prominent text: increased font size, displayed below the subtitle
    prominent_text: Optional[Text] = None

    # Actual card text
    text: Optional[Text] = None

    # Sub-text: decreased font size, displayed below the card text
    sub_text: Optional[Text] = None

    #
    # You can attach an action to a Card:
    #   an action is a URL linked to action text or action prominent text
    #   can be one of the internal deep links (CardAction) or an external url to a website
    #
    action: Optional[Union[CardAction, Text]] = None
    action_text: Optional[Text] = None
    action_prominent_text: Optional[Text] = None

    # URL of the card's icon
    icon_url: Optional[Text] = None

    #
    # Card can have a bullet-like list:
    #   a list section contains items and an optional title
    #   an item has a title and optional iconUrl
    #
    list_sections: Optional[List[ListSection]] = None


class Card(CamelModel):
    """Card to be sent to the companion app"""

    type: Text = GENERIC_DEFAULT
    version: int = CARD_VERSION

    data: CardData

    def __init__(
        self,
        type_=None,
        type: Text = None,
        version: Text = None,
        data: CardData = None,
        title_text: Text = None,
        type_description: Text = None,
        prominent_text: Text = None,
        text: Text = None,
        sub_text: Text = None,
        action: Text = None,
        action_text: Text = None,
        action_prominent_text: Text = None,
        icon_url: Text = None,
        list_sections: List[ListSection] = None,
    ) -> None:
        """
        Accept and ignore `type_` as positional argument for backward compatibility

        :param type_:
        :param type:
        :param version:
        :param data:
        :param title_text:
        :param type_description:
        :param prominent_text:
        :param text:
        :param sub_text:
        :param action:
        :param action_text:
        :param action_prominent_text:
        :param icon_url:
        :param list_sections:
        """
        data = data or CardData(
            title_text=title_text,
            type_description=type_description,
            prominent_text=prominent_text,
            text=text,
            sub_text=sub_text,
            action=action,
            action_text=action_text,
            action_prominent_text=action_prominent_text,
            icon_url=icon_url,
            list_sections=list_sections,
        )
        super().__init__(data=data)

    def __getattr__(self, attr):
        return getattr(self.data, attr)

    def with_action(
        self,
        action_text: Text,
        action: Union[CardAction, Text],
        action_prominent_text: Text = None,
        **kwargs
    ) -> "Card":
        """
        Add action to card

        :param action_text:
        :param action:
        :param action_prominent_text:
        :param kwargs:
        :return:
        """
        data = self.data.copy(
            update=dict(
                action_text=action_text,
                action_prominent_text=action_prominent_text,
                action=action.format(**kwargs),
            )
        )
        return self.copy(update=dict(data=data))

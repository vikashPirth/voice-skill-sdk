#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Skill invoke response"""

import copy
from enum import Enum
from typing import Any, Dict, Optional, List, Text, Union

from skill_sdk import i18n
from skill_sdk.i18n import Message
from skill_sdk.utils.util import CamelModel
from skill_sdk.responses.card import Card, ListSection
from skill_sdk.responses.command import Command
from skill_sdk.responses.result import Result
from skill_sdk.responses.task import ClientTask


class ResponseType(str, Enum):
    """
    Response types:

        TELL    pronounce the text on the device and end the session

        ASK     pronounce the text and wait for user's intent as response

        ASK_FREETEXT    pronounce the text and wait for user response as text

    """

    TELL = "TELL"
    ASK = "ASK"
    ASK_FREETEXT = "ASK_FREETEXT"


class PushNotification(CamelModel):
    """Messaging data to be sent to the client or app"""

    # The message
    message_payload: Optional[Text]

    # Target device name
    target_name: Optional[Text]


class SessionResponse(CamelModel):
    """Session attributes in the response"""

    attributes: Dict[Text, Text]


class SkillInvokeResponse(CamelModel):
    """Skill invoke response"""

    # Text to send to the device
    text: Union[Message, Text]

    # Response type
    type: ResponseType = ResponseType.TELL

    # Card to create
    card: Optional[Card]

    # Push notification to send
    push_notification: Optional[PushNotification]

    # Skill result data
    result: Optional[Result]

    # Device session
    session: Optional[SessionResponse]

    def __init__(
        self, text: Text, type_: ResponseType = None, result: Dict = None, **data: Any
    ) -> None:
        """
        Accept `text` and `type_` as positional arguments
            and `result` as dictionary for backward compatibility

        :param text:    text to pronounce
        :param type_:   response type
        :param data:
        """
        if "type" in data and type_ is not None:
            raise ValueError(
                f"Ambiguous response type: 'type_'={type_} and 'type='{data['type']}."
            )

        params: Dict[str, Any] = dict(text=text)
        if type_ is not None:
            params.update(type=type_)

        if result and isinstance(result, Dict):
            params.update(result=Result(result["data"] if "data" in result else result))

        super().__init__(**{**data, **params})

    def dict(self, *args, **kwargs) -> Dict[Text, Any]:
        """
        Dump the request into JSON suitable to be returned to the dialog manager.
        :param context: the context of the request
        """

        result = self.result or Result(dict())
        # Export string key and format parameters from Message object
        if isinstance(self.text, i18n.Message):
            result.update(
                key=self.text.key,
                value=self.text.value,
                args=self.text.args,
                kwargs=self.text.kwargs,
            )

        # Required properties
        resp: Dict[Text, Any] = dict()
        resp.update(type=self.type, text=self.text)

        # Optional properties
        if self.card:
            resp.update(card=self.card.dict())
        if result:
            resp.update(result=result.dict())
        if self.push_notification:
            resp.update(pushNotification=self.push_notification)
        if self.session:
            resp.update(session={"attributes": self.session.attributes})

        return resp

    def with_card(
        self,
        card: Card = None,
        *,
        icon_url: Text = None,
        title_text: Text = None,
        type_description: Text = None,
        image_url: Text = None,
        prominent_text: Text = None,
        action_prominent_text: Text = None,
        text: Text = None,
        sub_text: Text = None,
        media_url: Text = None,
        list_sections: List[ListSection] = None,
    ) -> "SkillInvokeResponse":
        """
        Attach Card to a response

        :param card:
        :param icon_url:
        :param title_text:
        :param type_description:
        :param image_url:
        :param prominent_text:
        :param action_prominent_text:
        :param text:
        :param sub_text:
        :param media_url:
        :param list_sections:
        :return:
        """
        return self.copy(
            update=dict(
                card=card
                or Card(
                    icon_url=icon_url,
                    title_text=title_text,
                    type_description=type_description,
                    image_url=image_url,
                    prominent_text=prominent_text,
                    action_prominent_text=action_prominent_text,
                    text=text,
                    sub_text=sub_text,
                    media_url=media_url,
                    list_sections=list_sections,
                )
            )
        )

    def with_command(self, command: Command) -> "SkillInvokeResponse":
        """
        Add a command to execute on the client

        :param command:
        :return:
        """
        result = Result(data=command.dict())
        return self.copy(update=dict(result=result))

    def with_notification(
        self,
        message: PushNotification = None,
        message_payload: Text = None,
        target_name: Text = None,
    ) -> "SkillInvokeResponse":
        """
        Add a command to execute on the client

        :param message:
        :param message_payload:
        :param target_name:
        :return:
        """
        message = message or PushNotification(
            message_payload=message_payload, target_name=target_name
        )
        return self.copy(update=dict(push_notification=message))

    def with_session(self, **attributes) -> "SkillInvokeResponse":
        """
        Add attributes (key -> value) to keep in session storage

            (valid only for ResponseType.ASK/ASK_FREETEXT:
             ResponseType.TELL immediately ends the session)

        :param attributes:
        :return:
        """

        if self.type == ResponseType.TELL:
            raise ValueError(f"Response type: {self.type} ends the session.")

        session = SessionResponse(attributes=attributes)
        return self.copy(update=dict(session=session))

    def with_task(self, task: ClientTask):
        """
        Add a delayed client task

        :param task:
        :return:
        """
        result = self.result or Result(data={})
        return self.copy(update=dict(result=result.with_task(task)))


def _enrich(response: SkillInvokeResponse) -> SkillInvokeResponse:
    """
    Post-process a skill invoke response:

        - If simple text is returned - convert to Response
        - If session attributes are present - add to response

    :param response:
    :return:
    """
    from skill_sdk.intents.request import r

    if isinstance(response, str):
        # Convert string response to Response object
        response = SkillInvokeResponse(text=response)

    #
    # Copy session attributes from global request,
    # unless response is TELL, that ends the session
    #
    if response.type != ResponseType.TELL and r.session.attributes:
        attributes = copy.deepcopy(r.session.attributes)
        return response.with_session(**attributes)

    return response

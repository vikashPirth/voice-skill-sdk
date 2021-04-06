#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Client tasks (delayed or scheduled)"""

import datetime
from enum import Enum
from typing import Any, Dict, Optional, Text

import isodate
from skill_sdk.util import CamelModel


class ReferenceType(Text, Enum):
    """Reference anchor: either end of the speech or beginning of the speech (when response is received)"""

    SPEECH_END = "SPEECH_END"
    THIS_RESPONSE = "THIS_RESPONSE"


class ExecuteAfter(CamelModel):
    """Command is executed after speech end with optional offset"""

    reference: ReferenceType = ReferenceType.SPEECH_END

    # Positive offset relative to reference given as duration
    offset: Optional[Text] = None


class ExecutionTime(CamelModel):
    """
    Exported as timestamp in ISO-8601 format, e.g. 2020-11-25T12:00:00Z
    """

    # Relative execution time
    execute_after: Optional[ExecuteAfter] = None

    # Absolute execution time
    execute_at: Optional[Text] = None

    @staticmethod
    def at(time: datetime.datetime) -> "ExecutionTime":
        return ExecutionTime(execute_at=time.isoformat())

    @staticmethod
    def after(
        event: ReferenceType = ReferenceType.SPEECH_END,
        offset: datetime.timedelta = datetime.timedelta(0),
    ) -> "ExecutionTime":
        return ExecutionTime(
            execute_after=ExecuteAfter(
                reference=event, offset=isodate.duration_isoformat(offset)
            )
        )


class InvokeData(CamelModel):
    """Intent invoke data: name, skill and parameters"""

    # Intent name
    intent: Text

    # Skill Id
    skill_id: Optional[Text] = None

    # Parameters (will be converted to intent invoke attributes)
    parameters: Dict[Text, Any] = {}


class DelayedClientTask(CamelModel):
    """
    Delayed (postponed or scheduled) task, that client executes upon receiving this response
    Standard use case is to invoke an intent after speech end

    """

    # Invoke data
    invoke_data: InvokeData

    # Invoke execution time (default - right after speech end)
    execution_time: ExecutionTime

    @staticmethod
    def invoke(intent: Text, skill_id: Text = None, **kwargs) -> "DelayedClientTask":
        """
        Create a task to invoke intent

            Execute "WEATHER__INTENT" in 10 seconds after speech end:
            >>>         response = Response("Weather forecast in 10 seconds.").with_task(
            >>>             ClientTask.invoke("WEATHER__INTENT")
            >>>                 .after(offset=datetime.timedelta(seconds=10))
            >>>         )


        :param intent:      Intent name to invoke
        :param skill_id:    Optional skill Id
        :param kwargs:      Key/values map converted into attributes for skill invocation
        :return:
        """
        invoke_data = InvokeData(intent=intent, skill_id=skill_id, parameters=kwargs)
        execution_time = ExecutionTime.after(ReferenceType.SPEECH_END)

        return DelayedClientTask(invoke_data=invoke_data, execution_time=execution_time)

    def at(self, time: datetime.datetime) -> "DelayedClientTask":
        """
        Schedule the task execution to particular time point

            Excetute the task in 10 seconds:
            >>> task.at(datetime.datetime.now() + datetime.timedelta(seconds=10))

        :param time:    Time point to execute the task
        :return:
        """
        return self.copy(update=dict(execution_time=ExecutionTime.at(time)))

    def after(
        self,
        event: ReferenceType = ReferenceType.SPEECH_END,
        offset: datetime.timedelta = datetime.timedelta(0),
    ) -> "DelayedClientTask":
        """
        Delay the task execution AND/OR change the reference point type

            Schedule the task to execute BEFORE speech starts:
            >>> task.after(ReferenceType.THIS_RESPONSE)

            To delay task execution by 10 seconds after speech ends:
            >>> task.after(ReferenceType.SPEECH_END, datetime.timedelta(seconds=10))

        :param event:   even reference type (SPEECH_END - after speech ends, THIS_RESPONSE - before speech starts)
        :param offset:  offset timedelta
        :return:
        """
        return self.copy(
            update=dict(execution_time=ExecutionTime.after(event=event, offset=offset))
        )


ClientTask = DelayedClientTask

# pyright: reportMissingImports=false

import logging
import os
from glob import iglob
from pathlib import Path


from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)

INDEX_FILE_PATH = str(Path.home() / ".ulauncher-glob-index")


def message(name, description):
    return RenderResultListAction(
        [
            ExtensionResultItem(
                name,
                description,
                icon="images/icon.png",
            )
        ]
    )


def create_item(filepath):
    return ExtensionResultItem(
        icon="images/icon.png",
        name=os.path.basename(filepath),
        description=filepath,
        on_enter=OpenAction(filepath),
    )


class DemoExtension(Extension):
    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

        filepaths = iglob(f"{str(Path.home())}/Pictures/**/*", recursive=True)

        index = open(INDEX_FILE_PATH, "w")

        for filepath in filepaths:
            index.write(f"{filepath}\n")


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):

        query = (event.get_argument() or "").lower()

        if not query:
            return message(
                name="Type a file or folder name", description="Example: image.jpg"
            )

        index = open(INDEX_FILE_PATH)
        filepaths = index.readlines()

        first_10_results = list(
            filter(
                lambda filepath: query in os.path.basename(filepath.lower()), filepaths
            )
        )[:10]

        items = [create_item(result) for result in first_10_results]

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=data["new_name"],
                    on_enter=HideWindowAction(),
                )
            ]
        )


if __name__ == "__main__":
    DemoExtension().run()

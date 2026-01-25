from src.packs import remove_packs
from src.click import click_img
from src.screen import find_img


def put_in_storage():
    click_img([("img/unchecked_box.png",)], [("img/checked_box.png",)])
    if find_img([{"path": "img/arrow_storage.png", "precise": True}]):
        click_img(
            [{"path": "img/arrow_storage.png", "precise": True}],
            wait_until_images_to_click_gone=True,
        )


def store_arcemon():
    remove_packs([{"path": "img/arcemon_building.png", "precise": True}])

    click_img([("img/arcemon_building.png",)], [("img/entreposer.png",)])
    click_img(
        [("img/entreposer.png",)],
        [("img/unchecked_box.png",), ("img/checked_box.png",)],
    )
    put_in_storage()


def store_monster():
    remove_packs([{"path": "img/monster_building.png", "precise": True}])

    click_img([("img/monster_building.png",)], [("img/invoque.png",)])
    click_img(
        [("img/invoque.png",)], [("img/unchecked_box.png",), ("img/checked_box.png",)]
    )
    put_in_storage()


def store_all(store_units_data):
    if store_units_data["monsters"]:
        store_monster()

    if store_units_data["arcemons"]:
        store_arcemon()

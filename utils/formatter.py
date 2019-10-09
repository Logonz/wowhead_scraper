import json
from pathlib import Path

from utils.paths import OUTPUT_DIR


class Formatter:
    lang: str
    lang_dir: Path

    def __call__(self, lang="en", f_type="npc", **kwargs):
        self.lang = lang
        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            print("Directory for language '{}' doesn't exist. Creating it...".format(self.lang))
            self.lang_dir.mkdir()

        if f_type == "item":
            self.__format_item_names()
        elif f_type == "npc":
            self.__format_npc_names()
        elif f_type == "object":
            self.__format_object_names()
        elif f_type == "quest":
            self.__format_quests()

    def __format_item_names(self):
        item_input = self.__load_json_file("item_data.json")
        with Path(self.lang_dir / "lookupItems.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("item")
            self.__write_id_to_string_table(g, item_input, table_name)

    def __format_npc_names(self):
        npc_input = self.__load_json_file("npc_data.json")
        with Path(self.lang_dir / "lookupNpcs.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name()
            self.__write_id_to_string_table(g, npc_input, table_name)

    def __write_id_to_string_table(self, g, data, table_name):
        g.write(table_name)
        for item in data:
            name = self.__filter_text(item["name"])
            g.write("[{}] = {},\n".format(item["id"], name))
        g.write("}\n")

    def __format_object_names(self):
        object_input = self.__load_json_file("object_data.json")
        with Path(self.lang_dir / "lookupObjects.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("object")
            g.write(table_name)

            for item in object_input:
                name = self.__filter_text(item["name"])
                if name.startswith("[") or name == "nil":
                    continue
                g.write("[{}] = {},\n".format(name, item["id"]))

            g.write("}\n")

    def __load_json_file(self, file_name: str):
        print("Loading '{}'...".format(file_name))
        with Path(self.lang_dir / file_name).open("r", encoding="utf-8") as f:
            data = json.load(f)
            data.sort(key=lambda k: int(k["id"]))
        print("Data contains {} entries".format(len(data)))
        return data

    def __format_quests(self):
        quest_input = self.__load_json_file("quest_data.json")
        with Path(self.lang_dir / "lookupQuests.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("quest")
            g.write(table_name)

            for item in quest_input:
                title = self.__filter_text(item["title"])
                objective = self.__filter_text(item["objective"])
                description = self.__filter_text(item["description"])

                g.write("[{id}] = {{{title}, {desc}, {obj}}},\n".format(id=item["id"], title=title,
                                                                        desc=description, obj=objective))

            g.write("}\n")

    def __get_table_name(self, target="npc"):
        lang = self.lang
        if target == "item":
            table_name = "LangItemLookup[\"{}\"] = {{\n"
        elif target == "npc":
            table_name = "LangNameLookup[\"{}\"] = {{\n"
        elif target == "object":
            table_name = "LangObjectLookup[\"{}\"] = {{\n"
        else:
            table_name = "LangQuestLookup[\"{}\"] = {{\n"
        if lang == "en":
            return table_name.format("enUS")
        elif lang == "de":
            return table_name.format("deDE")
        elif lang == "fr":
            return table_name.format("frFR")
        elif lang == "es":
            return table_name.format("esES")
        elif lang == "ru":
            return table_name.format("ruRU")
        elif lang == "cn":
            return table_name.format("zhCN")
        elif lang == "pt":
            return table_name.format("ptBR")
        else:
            raise ValueError("Language '{}' not supported for formatting!".format(lang))

    def __filter_text(self, text):
        text = text.replace("\\", "")
        text = text.replace("\"", "\\\"")
        if self.lang == "ru":
            text = text.replace("|3-6(<раса>)", "<раса>")
            text = text.replace("|3-1(<класс>)", "<класс>")
            text = text.replace("|3-2(<класс>)", "<класс>")
            text = text.replace("|3-6(<класс>)", "<класс>")

        if not text:
            return "nil"
        return "\"" + text + "\""


if __name__ == '__main__':
    formatter = Formatter()
    formatter("pt", "quest")
    # f("pt", "quest")

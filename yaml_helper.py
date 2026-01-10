import yaml

class LiteralString(str):
    """Строка, которая будет сериализована как литерал YAML (|)"""
    pass

def literal_string_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(LiteralString, literal_string_representer)

def yaml_string(text, style=None):
    """
    Создает строку с указанным стилем YAML.
    
    Параметры:
    - text: текст строки
    - style: 
        '|' - literal (сохраняет все переносы)
        '>' - folded (сворачивает одиночные переносы)
        None - обычная строка
    """
    class StyledString(str):
        pass
    
    def representer(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', str(data), style=style)
    
    yaml.add_representer(StyledString, representer)
    return StyledString(text)
def convert_to_literal_strings(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and '\n' in value:
                obj[key] = LiteralString(value)
            else:
                convert_to_literal_strings(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                convert_to_literal_strings(item)
            elif isinstance(item, str) and '\n' in item:
                obj[i] = LiteralString(item)

    return obj
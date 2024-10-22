import json
import re
import subprocess

import automatic_code_review_commons as commons


def review(config):
    path_source = config['path_source']
    changes = config['merge']['changes']
    rules = config['rules']
    comments = []

    for change in changes:
        new_path = change['new_path']
        path = path_source + "/" + new_path

        if not path.endswith(('.h', '.cpp')):
            continue

        objs = get_cpp_methods_json(path)

        for obj in objs:
            kind = obj['kind']
            name = obj['name']

            if kind == 'property':
                continue

            if name == 'Q_DECLARE_METATYPE' or name.startswith("__anon"):
                continue

            params = extract_parameters_from_signature(obj['dataLine'])

            for param in params:
                if param.strip() == "":
                    continue

                if "=" in param:
                    param = param[0:param.index('=')].strip()

                parts = param.split(" ")
                param_name = parts[len(parts) - 1]

                if param_name.endswith("&"):
                    continue

                for obj_regex in rules:
                    regex = obj_regex['regex']

                    if re.match(regex, param_name):
                        line_number = obj['line']
                        comment_description = obj_regex['message']
                        comment_description = comment_description.replace("${PARAM_NAME}", param_name)
                        comment_description = comment_description.replace("${FILE_PATH}", new_path)
                        comment_description = comment_description.replace("${LINE_NUMBER}", str(line_number))

                        comments.append(commons.comment_create(
                            comment_id=commons.comment_generate_id(comment_description),
                            comment_path=new_path,
                            comment_description=comment_description,
                            comment_snipset=True,
                            comment_end_line=line_number,
                            comment_start_line=line_number,
                            comment_language='c++',
                        ))

    print(json.dumps(comments))

    return comments


def remove_templates(param):
    while re.search(r'<[^<>]*>', param):
        param = re.sub(r'<[^<>]*>', '', param)
    return param


def extract_parameters_from_signature(signature):
    if "Q_ENUM" in signature:
        return []

    if "(" not in signature:
        return []

    part = signature[signature.rindex('(') + 1:]

    if ")" not in part:
        return []

    part = part[0:part.rindex(')')]
    part = part.strip()

    part = remove_templates(part)

    params = part.split(",")

    if "" in params:
        params.remove("")

    return params


def get_cpp_methods_json(file_name):
    cmd = ['ctags', '--output-format=json', '--fields=+n', '--c++-kinds=f', '--c++-kinds=+p', file_name]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception("ctags command error")

    retorno = result.stdout.split("\n")

    with open(file_name, 'r') as content:
        lines = content.readlines()

    objs = []
    for obj in retorno:
        if obj == "":
            continue

        obj = json.loads(obj)
        obj['dataLine'] = lines[obj['line'] - 1]
        objs.append(obj)

    return objs

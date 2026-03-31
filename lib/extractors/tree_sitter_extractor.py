"""
tree-sitter unified extractor.
Default support: C, JavaScript, TypeScript, Python
Extended support: Go, Java, Rust (requires additional install)
"""

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjs
import tree_sitter_typescript as tsts
import tree_sitter_c as tsc
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any


LANGUAGE_MODULES = {
    ".py": (tspython, "python"),
    ".js": (tsjs, "javascript"),
    ".jsx": (tsjs, "javascript"),
    ".ts": (tsts, "typescript"),
    ".tsx": (tsts, "typescript"),
    ".c": (tsc, "c"),
    ".h": (tsc, "c"),
    # Extended languages (optional)
    ".go": None,
    ".java": None,
    ".rs": None,
}


def get_parser(suffix: str) -> Parser | None:
    """Get parser for the given file suffix."""
    lang_info = LANGUAGE_MODULES.get(suffix)
    if lang_info is None:
        # Try loading optional languages
        try:
            if suffix == ".go":
                import tree_sitter_go as tsgo

                return Parser(Language(tsgo.language()))
            elif suffix == ".java":
                import tree_sitter_java as tsjava

                return Parser(Language(tsjava.language()))
            elif suffix == ".rs":
                import tree_sitter_rust as tsrust

                return Parser(Language(tsrust.language()))
        except ImportError:
            return None
    if lang_info:
        module, _ = lang_info
        return Parser(Language(module.language()))
    return None


def extract_structure(filepath: str) -> dict[str, Any]:
    """Extract code structure: functions, classes, imports."""
    path = Path(filepath)
    parser = get_parser(path.suffix)

    if parser is None:
        return {"error": f"Unsupported language: {path.suffix}", "file": filepath}

    source = path.read_bytes()
    tree = parser.parse(source)
    root = tree.root_node

    functions = []
    classes = []
    imports = []

    lang_name = LANGUAGE_MODULES.get(path.suffix, (None, "unknown"))[1]

    if lang_name == "python":
        functions, classes, imports = _extract_python_elements(root, source)
    elif lang_name in ("javascript", "typescript"):
        functions, classes, imports = _extract_js_elements(root, source)
    elif lang_name == "c":
        functions, imports = _extract_c_elements(root, source)

    return {
        "file": filepath,
        "language": lang_name,
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }


def _extract_python_elements(root, source: bytes) -> tuple[list, list, list]:
    """Extract Python functions, classes, and imports."""
    functions = []
    classes = []
    imports = []

    for node in root.children:
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                    "args": _extract_python_args(node, source),
                })
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                class_info = {
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                    "bases": _extract_python_bases(node, source),
                    "methods": [],
                }
                # Extract methods from class body
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        # Handle both plain and decorated function definitions
                        if child.type == "function_definition":
                            method_name = child.child_by_field_name("name")
                            if method_name:
                                class_info["methods"].append({
                                    "name": source[method_name.start_byte:method_name.end_byte].decode(),
                                    "line": child.start_point[0] + 1,
                                    "args": _extract_python_args(child, source),
                                    "decorators": [],
                                })
                        elif child.type == "decorated_definition":
                            # Extract decorators and the underlying function
                            decorators = []
                            func_node = None
                            for sub in child.children:
                                if sub.type == "decorator":
                                    dec_text = source[sub.start_byte:sub.end_byte].decode()
                                    decorators.append(dec_text)
                                elif sub.type == "function_definition":
                                    func_node = sub
                            if func_node:
                                method_name = func_node.child_by_field_name("name")
                                if method_name:
                                    class_info["methods"].append({
                                        "name": source[method_name.start_byte:method_name.end_byte].decode(),
                                        "line": func_node.start_point[0] + 1,
                                        "args": _extract_python_args(func_node, source),
                                        "decorators": decorators,
                                    })
                classes.append(class_info)
        elif node.type == "import_statement":
            imports.extend(_extract_python_import(node, source))
        elif node.type == "import_from_statement":
            imports.extend(_extract_python_from_import(node, source))

    return functions, classes, imports


def _extract_python_args(func_node, source: bytes) -> list[str]:
    """Extract function argument names."""
    args = []
    params = func_node.child_by_field_name("parameters")
    if params:
        for child in params.children:
            if child.type == "identifier":
                args.append(source[child.start_byte:child.end_byte].decode())
            elif child.type == "typed_parameter":
                name = child.child_by_field_name("name")
                if name:
                    args.append(source[name.start_byte:name.end_byte].decode())
    return args


def _extract_python_bases(class_node, source: bytes) -> list[str]:
    """Extract class base names."""
    bases = []
    arg_list = class_node.child_by_field_name("superclasses")
    if arg_list:
        for child in arg_list.children:
            if child.type == "identifier":
                bases.append(source[child.start_byte:child.end_byte].decode())
    return bases


def _extract_python_import(node, source: bytes) -> list[dict]:
    """Extract import statement."""
    imports = []
    for child in node.children:
        if child.type == "dotted_name":
            imports.append({
                "module": source[child.start_byte:child.end_byte].decode(),
                "line": node.start_point[0] + 1,
            })
        elif child.type == "aliased_import":
            name = child.child_by_field_name("name")
            if name:
                imports.append({
                    "module": source[name.start_byte:name.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                })
    return imports


def _extract_python_from_import(node, source: bytes) -> list[dict]:
    """Extract from import statement."""
    imports = []
    module = node.child_by_field_name("module_name")
    module_name = source[module.start_byte:module.end_byte].decode() if module else ""

    for child in node.children:
        if child.type == "dotted_name" and child != module:
            imports.append({
                "module": module_name,
                "names": [source[child.start_byte:child.end_byte].decode()],
                "line": node.start_point[0] + 1,
            })
        elif child.type == "import_list":
            names = []
            for item in child.children:
                if item.type == "identifier":
                    names.append(source[item.start_byte:item.end_byte].decode())
            if names:
                imports.append({
                    "module": module_name,
                    "names": names,
                    "line": node.start_point[0] + 1,
                })
    return imports


def _extract_js_elements(root, source: bytes) -> tuple[list, list, list]:
    """Extract JS/TS functions, classes, and imports."""
    functions = []
    classes = []
    imports = []

    # Simplified extraction for JS/TS
    for node in root.children:
        if node.type in ("function_declaration", "function_expression", "arrow_function"):
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append({
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                })
        elif node.type == "class_declaration":
            name_node = node.child_by_field_name("name")
            if name_node:
                class_info = {
                    "name": source[name_node.start_byte:name_node.end_byte].decode(),
                    "line": node.start_point[0] + 1,
                    "methods": [],
                }
                # Extract methods from class body
                body = node.child_by_field_name("body")
                if body:
                    for child in body.children:
                        if child.type in ("method_definition", "function_declaration"):
                            method_name = child.child_by_field_name("name")
                            if method_name:
                                class_info["methods"].append({
                                    "name": source[method_name.start_byte:method_name.end_byte].decode(),
                                    "line": child.start_point[0] + 1,
                                })
                classes.append(class_info)
        elif node.type == "import_statement":
            imports.append({
                "module": "import",
                "line": node.start_point[0] + 1,
            })

    return functions, classes, imports


def _extract_c_elements(root, source: bytes) -> tuple[list, list]:
    """Extract C functions and includes."""
    functions = []
    imports = []

    for node in root.children:
        if node.type == "function_definition":
            # Find function name - handle both simple and pointer-returning functions
            func_name = None
            for child in node.children:
                if child.type == "function_declarator":
                    # Simple function: function_declarator contains identifier directly
                    for sub in child.children:
                        if sub.type == "identifier":
                            func_name = source[sub.start_byte:sub.end_byte].decode()
                            break
                elif child.type == "pointer_declarator":
                    # Pointer-returning function: function_declarator is nested inside pointer_declarator
                    for sub in child.children:
                        if sub.type == "function_declarator":
                            for fd_child in sub.children:
                                if fd_child.type == "identifier":
                                    func_name = source[fd_child.start_byte:fd_child.end_byte].decode()
                                    break
            if func_name:
                functions.append({
                    "name": func_name,
                    "line": node.start_point[0] + 1,
                })
        elif node.type == "preproc_include":
            imports.append({
                "module": "include",
                "line": node.start_point[0] + 1,
            })

    return functions, imports
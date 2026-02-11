"""
Fetches http://localhost:8080/v3/api-docs
Walks each path + operation
For 200 application/json responses, it:

Builds a concrete body from example fields if available (fallback: typed placeholders)
Adds bodyMatchers: type checks for strings/ints; regex for email format
Resolves path variables ({id}) using parameter examples (fallbacks: 1 for ints, "sample" for strings)


Writes one Groovy contract per operation under
src/test/resources/contracts/generated/…

"""

# scripts/openapi-to-scc.py

import json, os, re, sys
from urllib.request import urlopen, Request

# -------- settings --------
OPENAPI_URL = os.environ.get("OPENAPI_URL", "http://localhost:8080/v3/api-docs")
OUT_DIR = os.environ.get("OUT_DIR", "src/test/resources/contracts/generated")
# --------------------------

def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)

def sanitize_path_for_filename(p):
    # e.g. /users/{id} -> users_id
    return re.sub(r'[^a-zA-Z0-9]+', '_', p).strip('_')

def placeholder_for_type(schema):
    t = schema.get('type')
    fmt = schema.get('format')
    if fmt == 'email':
        return "john@example.com"
    if t == 'integer' or t == 'number':
        return 1
    if t == 'boolean':
        return True
    # object/array/unknown -> simple fallback
    return "sample"

def matcher_for_type(schema, json_path):
    t = schema.get('type')
    fmt = schema.get('format')
    if fmt == 'email':
        return f"jsonPath('{json_path}', byRegex(/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/))"
    if t in ('integer', 'number'):
        return f"jsonPath('{json_path}', byType())"
    if t == 'boolean':
        return f"jsonPath('{json_path}', byType())"
    if t == 'array' or t == 'object':
        return f"jsonPath('{json_path}', byType())"
    # string or unknown
    return f"jsonPath('{json_path}', byType())"

def build_example_and_matchers(schema, base_path='$'):
    """
    Build a concrete example body (dict) and a list of bodyMatchers lines.
    Prefer 'example' if present, fallback by 'type/format'.
    """
    body = None
    matchers = []
    if not schema:
        return body, matchers

    t = schema.get('type')
    if 'example' in schema:
        body = schema['example']
        # still add a byType matcher for root when useful
        if t in ('object', 'array'):
            matchers.append(matcher_for_type(schema, base_path))
        return body, matchers

    if t == 'object':
        props = schema.get('properties', {})
        body = {}
        for name, prop in props.items():
            jp = f"{base_path}.{name}"
            ex = prop.get('example', None)
            if ex is None:
                # recurse on nested
                bt, ms = build_example_and_matchers(prop, jp)
                body[name] = bt if bt is not None else placeholder_for_type(prop)
                matchers.extend(ms)
                matchers.append(matcher_for_type(prop, jp))
            else:
                body[name] = ex
                matchers.append(matcher_for_type(prop, jp))
        return body, matchers

    if t == 'array':
        items = schema.get('items', {})
        item_body, item_matchers = build_example_and_matchers(items, f"{base_path}[0]")
        body = [item_body if item_body is not None else placeholder_for_type(items)]
        matchers.extend(item_matchers)
        matchers.append(matcher_for_type(schema, base_path))
        return body, matchers

    # primitives
    body = placeholder_for_type(schema)
    matchers.append(matcher_for_type(schema, base_path))
    return body, matchers

def example_for_path_var(name, param):
    schema = (param or {}).get('schema', {})
    ex = (param or {}).get('example')
    if ex is not None:
        return str(ex)
    t = schema.get('type')
    if t in ('integer','number'):
        return '1'
    return '1' if name.lower()=='id' else 'sample'

def resolve_url_path(path, params):
    # replace {var} with example values
    def repl(m):
        var = m.group(1)
        p = next((p for p in params if p.get('name')==var and p.get('in')=='path'), None)
        return example_for_path_var(var, p)
    return re.sub(r'\{([^}]+)\}', repl, path)

def to_contract_filename(method, path):
    return f"{method.lower()}_{sanitize_path_for_filename(path)}_200.groovy"

def emit_groovy_contract(file_path, method, url_path, body_dict, matchers_lines, description="Auto-generated from OpenAPI"):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("org.springframework.cloud.contract.spec.Contract.make {\n")
        f.write(f"  description \"{description}\"\n\n")
        f.write("  request {\n")
        f.write(f"    method {method.upper()}()\n")
        f.write(f"    urlPath(\"{url_path}\")\n")
        f.write("  }\n\n")
        f.write("  response {\n")
        f.write("    status OK()\n")
        f.write("    headers { contentType(applicationJson()) }\n")
        if body_dict is not None:
            # pretty JSON-ish Groovy map
            def groovy_obj(obj, indent=6):
                sp = ' ' * indent
                if isinstance(obj, dict):
                    items = []
                    for k,v in obj.items():
                        items.append(f"{sp}{k}: {groovy_obj(v, indent+2)}")
                    return "{\n" + ",\n".join(items) + f"\n{' '*(indent-2)}}}"
                elif isinstance(obj, list):
                    items = [groovy_obj(v, indent+2) for v in obj]
                    return "[ " + ", ".join(items) + " ]"
                elif isinstance(obj, str):
                    return f"\"{obj}\""
                elif isinstance(obj, bool):
                    return "true" if obj else "false"
                else:
                    return str(obj)

            f.write("    body(\n")
            f.write(f"{groovy_obj(body_dict, indent=6)}\n")
            f.write("    )\n")
        if matchers_lines:
            f.write("    bodyMatchers {\n")
            for line in matchers_lines:
                f.write(f"      {line}\n")
            f.write("    }\n")
        f.write("  }\n")
        f.write("}\n")

def main():
    print(f"[openapi-to-scc] Fetching {OPENAPI_URL} ...")
    req = Request(OPENAPI_URL, headers={'Accept': 'application/json'})
    with urlopen(req) as resp:
        spec = json.loads(resp.read().decode('utf-8'))

    ensure_dir(OUT_DIR)
    # optional: clear previously generated files
    for fn in os.listdir(OUT_DIR):
        if fn.endswith(".groovy"):
            try: os.remove(os.path.join(OUT_DIR, fn))
            except: pass

    paths = spec.get('paths', {})
    components = spec.get('components', {})
    schemas = components.get('schemas', {})

    total = 0
    for path, ops in paths.items():
        for method, op in ops.items():
            if method.lower() not in ('get','post','put','delete','patch'):
                continue
            responses = op.get('responses', {})
            r200 = responses.get('200') or responses.get('201')
            if not r200:  # only generate for success codes here
                continue
            content = (r200.get('content') or {}).get('application/json') or {}
            schema = content.get('schema')
            if not schema:
                body_dict, matchers = None, []
            else:
                # resolve $ref
                def deref(s):
                    if isinstance(s, dict) and '$ref' in s:
                        ref = s['$ref']  # e.g. "#/components/schemas/UserDto"
                        parts = ref.split('/')
                        name = parts[-1]
                        return schemas.get(name, {})
                    return s
                schema = deref(schema)
                body_dict, matchers = build_example_and_matchers(schema)

            # path parameter examples
            params = op.get('parameters', [])
            url_path = resolve_url_path(path, params)

            filename = to_contract_filename(method, path)
            out_file = os.path.join(OUT_DIR, filename)
            emit_groovy_contract(out_file, method, url_path, body_dict, matchers,
                                 description=f"{method.upper()} {path} (auto-generated)")
            total += 1
            print(f"[openapi-to-scc] Wrote {out_file}")

    print(f"[openapi-to-scc] Done. Generated {total} contract(s) in {OUT_DIR}")

if __name__ == "__main__":
    main()

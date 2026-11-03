"""Categorize residual upstream-matching added lines (nows) per approach/release."""
import sys, os, re, collections, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contamination as C
orig_dir, fmap_path = sys.argv[1:3]
rels = [x.split("=",1) for x in sys.argv[3].split(",")]
apps = [x.split("=",1) for x in sys.argv[4:]]
fmap = C.parse_file_map(fmap_path)
def cat(k):
    if "__construct" in k: return "ctor (__construct call/decl)"
    if "__DIR__" in k: return "__DIR__"
    if re.search(r"str_(contains|starts_with|ends_with)\(", k): return "str_contains/starts/ends_with"
    if "??" in k: return "?? operator"
    if not re.search(r"[;{}]$|\)$|:$", k) or k.endswith(",") or k.endswith("("): return "multi-line reformat fragment"
    return "other"
res = {}
for rel, root in rels:
    for name, pat in apps:
        c = collections.Counter()
        for f in sorted(x for x in os.listdir(orig_dir) if x.endswith(".php")):
            sid = f[:-4]; orig = C.read(os.path.join(orig_dir, f))
            paths, st = C.resolve_upstream(sid, fmap[sid], root, len(orig.splitlines()))
            if st not in ("same_path","relocated"): continue
            op = pat.replace("{id}", sid)
            if not os.path.isfile(op): continue
            up = "\n".join(C.read(p) for p in paths)
            g = C.lines_of(orig,"nows"); gs=set(g); gred={C.reduce_trivial(x,"nows") for x in g}; us=set(C.lines_of(up,"nows"))
            for k in C.lines_of(C.read(op),"nows"):
                if k in gs or k not in us: continue
                if C.reduce_trivial(k,"nows") in gred: c["trivial (visibility/brace)"] += 1
                else: c[cat(k)] += 1
        res[rel+"|"+name] = dict(c)
        print(rel, name, sum(c.values()), dict(c.most_common()))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hit_categories.json"), "w"), indent=1)

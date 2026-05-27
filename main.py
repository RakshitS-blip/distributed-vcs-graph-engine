import hashlib
import time
import json
import os
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Metadata for Interactive API Documentation
app = FastAPI(
    title="Topological Distributed VCS Architecture Engine",
    description="A high-performance, content-addressable version control system simulator executing immutable SHA-1 graph state transitions.",
    version="1.0.0",
    docs_url="/docs",  
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Middleware to prevent unhandled 500 crashes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": f"Low-Level Kernel Interruption: {str(exc)}"}
    )

DB_FILE = "vcs_object_store.json"

def load_system_state():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "object_store": {},
        "refs": {"HEAD": None, "active_branch": "main", "branches": {"main": None}},
        "logs": []
    }

def save_system_state(state):
    with open(DB_FILE, "w") as f:
        json.dump(state, f, indent=4)

class CommitRequest(BaseModel):
    message: str = Field(..., example="feat: extend modular interface parameters")
    content: str = Field(..., example="print('Systems Core initialized')")

class BranchRequest(BaseModel):
    name: str = Field(..., example="feature-sharding")

class CheckoutRequest(BaseModel):
    target: str = Field(..., example="main")

class MergeRequest(BaseModel):
    source_branch: str = Field(..., example="feature-sharding")

def hash_object(state, content: str, obj_type: str = "blob") -> str:
    header = f"{obj_type} {len(content)}\0"
    full_data = header + content
    sha1 = hashlib.sha1(full_data.encode('utf-8')).hexdigest()
    state["object_store"][sha1] = {"type": obj_type, "content": content}
    return sha1

@app.post("/commit", summary="Record Immutable State Matrix (Commit)")
def create_commit(data: CommitRequest):
    state = load_system_state()
    if not data.content.strip():
        return {"status": "error", "message": "Staged workspace buffers cannot be empty"}

    blob_sha = hash_object(state, data.content, "blob")
    tree_content = f"100644 blob {blob_sha}\tindex.txt"
    tree_sha = hash_object(state, tree_content, "tree")

    active_branch = state["refs"]["active_branch"]
    parent_sha = state["refs"]["branches"].get(active_branch)

    timestamp = int(time.time())
    commit_metadata = (
        f"tree {tree_sha}\n"
        f"parent {parent_sha if parent_sha else 'None'}\n"
        f"date {timestamp}\n"
        f"author Academic-Research-Engine\n\n"
        f"{data.message}"
    )
    commit_sha = hash_object(state, commit_metadata, "commit")

    state["refs"]["branches"][active_branch] = commit_sha
    state["refs"]["HEAD"] = commit_sha

    log_entry = f"[{time.strftime('%H:%M:%S', time.localtime(timestamp))}] Synchronized state {commit_sha[:7]} on branch '{active_branch}'."
    state["logs"].append(log_entry)

    save_system_state(state)
    return {"status": "success", "current_head": commit_sha}

@app.post("/branch", summary="Initialize Parallel DAG Timeline (Branch)")
def create_branch(data: BranchRequest):
    state = load_system_state()
    branch_name = data.name.strip().replace(" ", "-")

    if not branch_name:
        return {"status": "error", "message": "Reference label identifier mismatch"}
    if branch_name in state["refs"]["branches"]:
        return {"status": "error", "message": f"Branch timeline Reference '{branch_name}' already exists"}

    current_head = state["refs"]["HEAD"]
    state["refs"]["branches"][branch_name] = current_head

    state["logs"].append(f"[*] Diverged graph thread '{branch_name}' tracking commit {current_head[:7] if current_head else 'None'}")
    save_system_state(state)
    return {"status": "success"}

@app.post("/checkout", summary="Topological Jump to Target Reference (Checkout)")
def checkout(data: CheckoutRequest):
    state = load_system_state()
    target = data.target.strip()

    if target in state["refs"]["branches"]:
        state["refs"]["active_branch"] = target
        commit_sha = state["refs"]["branches"][target]
        state["refs"]["HEAD"] = commit_sha
        state["logs"].append(f"[*] Context switched to branch reference pointer '{target}'")
    elif target in state["object_store"] and state["object_store"][target]["type"] == "commit":
        commit_sha = target
        state["refs"]["HEAD"] = commit_sha
        state["logs"].append(f"[*] Navigated to isolated head vertex snapshot {target[:7]}")
    else:
        return {"status": "error", "message": "Graph traversal failure: Target hash pointer missing"}

    file_content = ""
    if commit_sha:
        lines = state["object_store"][commit_sha]["content"].split("\n")
        tree_sha = [line.split()[1] for line in lines if line.startswith("tree")][0]
        tree_text = state["object_store"][tree_sha]["content"]
        blob_sha = tree_text.split()[2]
        file_content = state["object_store"][blob_sha]["content"]

    save_system_state(state)
    return {"status": "success", "content": file_content, "active_branch": state["refs"]["active_branch"], "current_head": commit_sha}

@app.post("/merge", summary="Execute Structural Three-Way Merge Topology")
def merge_branches(data: MergeRequest):
    state = load_system_state()
    active_branch = state["refs"]["active_branch"]
    source_branch = data.source_branch.strip()

    if source_branch not in state["refs"]["branches"]:
        return {"status": "error", "message": f"Source reference tracking matrix mapping missing"}
    if source_branch == active_branch:
        return {"status": "error", "message": "Topological loop paradox: Cannot self-merge identical states"}

    target_sha = state["refs"]["branches"][active_branch]
    source_sha = state["refs"]["branches"][source_branch]

    if not source_sha:
        return {"status": "error", "message": "Divergent timeline source buffer evaluates to Null"}
    if not target_sha:
        state["refs"]["branches"][active_branch] = source_sha
        state["refs"]["HEAD"] = source_sha
        state["logs"].append(f"[*] Fast-forward matrix merge compiled for branch '{source_branch}'")
        save_system_state(state)
        return {"status": "success"}

    t_lines = state["object_store"][target_sha]["content"].split("\n")
    t_tree = [l.split()[1] for l in t_lines if l.startswith("tree")][0]
    t_blob = state["object_store"][t_tree]["content"].split()[2]
    t_content = state["object_store"][t_blob]["content"]

    s_lines = state["object_store"][source_sha]["content"].split("\n")
    s_tree = [l.split()[1] for l in s_lines if l.startswith("tree")][0]
    s_blob = state["object_store"][s_tree]["content"].split()[2]
    s_content = state["object_store"][s_blob]["content"]

    merged_content = f"{t_content}\n# --- TOPOLOGICAL CONFLICT INTEGRATION MATRIX ---\n{s_content}"
    merged_blob_sha = hash_object(state, merged_content, "blob")

    tree_content = f"100644 blob {merged_blob_sha}\tindex.txt"
    merged_tree_sha = hash_object(state, tree_content, "tree")

    timestamp = int(time.time())
    commit_metadata = (
        f"tree {merged_tree_sha}\n"
        f"parent {target_sha}\n"
        f"parent2 {source_sha}\n"
        f"date {timestamp}\n"
        f"author Merge-Coordinator-Engine\n\n"
        f"merge: integrated '{source_branch}' into '{active_branch}'"
    )
    merge_commit_sha = hash_object(state, commit_metadata, "commit")

    state["refs"]["branches"][active_branch] = merge_commit_sha
    state["refs"]["HEAD"] = merge_commit_sha
    state["logs"].append(f"[M] Consolidated Unified Vertex Head {merge_commit_sha[:7]} generated.")

    save_system_state(state)
    return {"status": "success"}

@app.get("/graph", summary="Fetch Adjacency Map Matrix Metadata")
def get_graph():
    state = load_system_state()
    nodes = []
    edges = []

    for sha, obj in state["object_store"].items():
        if obj.get("type") == "commit":
            commit_content = obj.get("content", "")
            lines = commit_content.split("\n")

            msg = lines[-1] if lines[-1] else "Commit"
            short_sha = sha[:7]

            branch_labels = [b for b, head in state["refs"]["branches"].items() if head == sha]
            label_suffix = f" [{', '.join(branch_labels)}]" if branch_labels else ""
            label = f"💬 {msg}{label_suffix}\n({short_sha})"

            is_head = (state["refs"]["HEAD"] == sha)

            nodes.append({
                "id": sha,
                "label": label,
                "color": {"background": "#2563eb" if is_head else "#1e293b", "border": "#60a5fa" if is_head else "#475569"},
                "font": {"color": "#ffffff", "face": "monospace", "size": 11},
                "shape": "box",
                "borderWidth": 2 if is_head else 1
            })

            parent_line = [l for l in lines if l.startswith("parent ")]
            if parent_line:
                p_sha = parent_line[0].split()[1]
                if p_sha != "None" and p_sha in state["object_store"]:
                    edges.append({"from": p_sha, "to": sha, "arrows": "to", "color": {"color": "#4b5563"}, "smooth": {"type": "cubicBezier"}})

            parent2_line = [l for l in lines if l.startswith("parent2 ")]
            if parent2_line:
                p2_sha = parent2_line[0].split()[1]
                if p2_sha in state["object_store"]:
                    edges.append({"from": p2_sha, "to": sha, "arrows": "to", "color": {"color": "#3b82f6", "width": 2}, "style": "dashed", "smooth": {"type": "cubicBezier"}})

    return {"nodes": nodes, "edges": edges, "refs": state["refs"], "logs": state["logs"]}

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en" class="h-full bg-slate-950 text-slate-100">
    <head>
        <meta charset="UTF-8">
        <title>Distributed Topological Graph Version Control Core</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    </head>
    <body class="h-full flex flex-col font-sans overflow-hidden">
        <header class="border-b border-slate-800 bg-slate-900/60 p-4 flex justify-between items-center backdrop-blur-md">
            <div class="flex items-center gap-3">
                <div class="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                <h1 class="text-sm font-black tracking-widest text-slate-200 font-mono">DISTRIBUTED-VCS // TOPOLOGICAL-GRAPH-ENGINE Matrix-v1.0</h1>
            </div>
            <div class="flex gap-3">
                <a href="/docs" target="_blank" class="text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 px-3 py-1 rounded text-slate-400 hover:text-slate-200 transition-all">Interactive Core API Docs ➔</a>
                <span id="branchBadge" class="text-xs font-bold text-blue-400 font-mono bg-blue-950/60 border border-blue-900 px-3 py-1 rounded">BRANCH: main</span>
            </div>
        </header>

        <main class="flex-1 flex overflow-hidden">
            <div class="w-[360px] border-r border-slate-800 p-5 flex flex-col gap-4 bg-slate-900/20 overflow-y-auto">
                <div>
                    <label class="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">File System Workspace (index.txt)</label>
                    <textarea id="fileContent" class="w-full h-28 bg-slate-950 border border-slate-800 rounded p-2.5 font-mono text-xs text-slate-200 resize-none focus:outline-none focus:border-blue-500" placeholder="Type transactional tracking edits..."></textarea>
                </div>
                <div>
                    <label class="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">Commit Header Message</label>
                    <input id="commitMessage" type="text" class="w-full bg-slate-950 border border-slate-800 rounded p-2.5 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500" placeholder="e.g., feat: core internal structures">
                </div>
                <button onclick="commitState()" class="w-full bg-blue-600 hover:bg-blue-500 font-mono font-bold text-xs py-3 rounded transition-all active:scale-[0.99]">
                    EXECUTE STAGED COMMIT
                </button>

                <div class="border-t border-slate-800 my-1"></div>

                <div>
                    <label class="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">Create New DAG Branch</label>
                    <div class="flex gap-2">
                        <input id="newBranchName" type="text" class="flex-1 bg-slate-950 border border-slate-800 rounded p-2 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500" placeholder="e.g., feature-login">
                        <button onclick="createNewBranch()" class="bg-slate-800 hover:bg-slate-700 text-xs px-3 font-mono font-bold rounded">Create</button>
                    </div>
                </div>

                <div>
                    <label class="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">Active Branch Branches Dropdown</label>
                    <select id="branchSelector" onchange="switchBranchOrCommit(this.value)" class="w-full bg-slate-950 border border-slate-800 rounded p-2 font-mono text-xs text-slate-300 focus:outline-none focus:border-blue-500">
                        <option value="main">main</option>
                    </select>
                </div>

                <div class="border-t border-slate-800 my-2"></div>
                <div>
                    <label class="block text-[10px] font-mono uppercase tracking-wider text-slate-400 mb-1.5">Integrate Remote Branch Changes (Merge)</label>
                    <div class="flex gap-2">
                        <input id="mergeSourceInput" type="text" class="flex-1 bg-slate-950 border border-slate-800 rounded p-2 font-mono text-xs text-slate-200 focus:outline-none focus:border-blue-500" placeholder="e.g., feature-auth">
                        <button onclick="executeMerge()" class="bg-blue-600 hover:bg-blue-500 text-xs px-3 font-mono font-bold rounded">Merge</button>
                    </div>
                </div>
            </div>

            <div class="flex-1 flex flex-col bg-slate-950">
                <div class="flex-1 relative border-b border-slate-800/60 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px]">
                    <div class="absolute top-3 left-3 z-10 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded text-[10px] font-mono text-slate-400">
                        Interactive Commit DAG Layout (Click node to trigger 'git checkout')
                    </div>
                    <div id="networkCanvas" class="w-full h-full"></div>
                </div>

                <div class="h-44 bg-slate-950 p-4 border-t border-slate-800 flex flex-col font-mono">
                    <div class="text-[10px] uppercase tracking-widest text-slate-500 mb-2 font-bold">Low-Level System Diagnostic Trace Logs</div>
                    <div id="consoleLogs" class="flex-1 overflow-y-auto text-xs text-green-400 space-y-1 bg-slate-900/40 p-3 rounded border border-slate-900">
                        [00:00:00] High-Performance Object Graph Initialized and online.
                    </div>
                </div>
            </div>
        </main>

        <script>
            let network = null;

            async function refreshGraph() {
                const res = await fetch('/graph');
                const data = await res.json();

                document.getElementById('branchBadge').innerText = `ACTIVE BRANCH: ${data.refs.active_branch}`;

                const selector = document.getElementById('branchSelector');
                selector.innerHTML = "";
                Object.keys(data.refs.branches).forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b;
                    opt.innerText = `Branch: ${b}`;
                    if(b === data.refs.active_branch) opt.selected = true;
                    selector.appendChild(opt);
                });

                const logsDiv = document.getElementById('consoleLogs');
                logsDiv.innerHTML = data.logs.map(log => `<div>${log}</div>`).join('');
                logsDiv.scrollTop = logsDiv.scrollHeight;

                const container = document.getElementById('networkCanvas');
                const graphData = { nodes: new vis.DataSet(data.nodes), edges: new vis.DataSet(data.edges) };
                const options = {
                    physics: { solver: 'repulsion', repulsion: { nodeDistance: 120, centralGravity: 0.1 } },
                    interaction: { hover: true }
                };

                network = new vis.Network(container, graphData, options);
                network.on("click", async function (params) {
                    if (params.nodes.length > 0) {
                        switchBranchOrCommit(params.nodes[0]);
                    }
                });
            }

            async function commitState() {
                const content = document.getElementById('fileContent').value;
                const message = document.getElementById('commitMessage').value;
                if(!content || !message) return alert("Please fill standard input tracking arrays before staging commit.");

                const response = await fetch('/commit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message, content })
                });
                const data = await response.json();
                if (data.status === "error") alert(data.message);

                document.getElementById('commitMessage').value = "";
                refreshGraph();
            }

            async function createNewBranch() {
                const nameName = document.getElementById('newBranchName').value;
                if(!nameName) return alert("Specify valid string name arrays.");

                const res = await fetch('/branch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: nameName })
                });
                const d = await res.json();
                if(d.status === "error") alert(d.message);

                document.getElementById('newBranchName').value = "";
                refreshGraph();
            }

            async function switchBranchOrCommit(targetRef) {
                const res = await fetch('/checkout', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ target: targetRef })
                });
                const d = await res.json();
                if(d.status === "success") {
                    document.getElementById('fileContent').value = d.content;
                    refreshGraph();
                } else {
                    alert(d.message);
                }
            }

            async function executeMerge() {
                const source = document.getElementById('mergeSourceInput').value.trim();
                if(!source) return alert("Specify target source reference.");

                const res = await fetch('/merge', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ source_branch: source })
                });
                const d = await res.json();
                if(d.status === "error") alert(d.message);

                document.getElementById('mergeSourceInput').value = "";
                refreshGraph();
            }

            window.onload = refreshGraph;
        </script>
    </body>
    </html>
    """

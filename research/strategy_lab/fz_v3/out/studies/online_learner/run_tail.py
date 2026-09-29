"""run_tail.py - a helper worker for the fit stage: runs the jobs the primary driver (run_online.py --stage fit) has not written yet,
cheapest first (the reverse of the driver's order), one at a time, skipping any job whose checkpoint appears meanwhile. Same
run_online.run_job, same outputs; started when a core was free (gate_family finished) so the fit stage ends sooner. Log run_tail_<tf>.log."""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_online as R
tf = sys.argv[1]
specs = {d: R.load_spec(tf, d) for d in R.O.DESIGNS}
todo = [j for j in R.jobs(tf) if not os.path.exists(os.path.join(R.RES, tf, "jobs", j["id"] + ".pkl"))]
cost = lambda j: (0 if j["cfg"]["design"] == "full" else 1, j["cfg"]["cadence_k"], 0 if j["cfg"]["learner"] in ("logts", "hgb_reg", "hgb_cls") else 1)
todo.sort(key=cost, reverse=True)
print(f"[{tf}] tail worker: {len(todo)} jobs not yet written", flush=True)
t0 = time.time()
for j in todo:
    if os.path.exists(os.path.join(R.RES, tf, "jobs", j["id"] + ".pkl")): print(f"[{tf}] tail skip {j['id']} (written meanwhile)", flush=True); continue
    r = R.run_job(tf, j, specs[j["cfg"]["design"]])
    print(f"[{tf}] tail job {r['id']:<48} {r['seconds']:8.1f}s heads {r['heads']}  ({time.time() - t0:.0f}s elapsed)", flush=True)
print(f"[{tf}] tail worker done in {time.time() - t0:.0f}s", flush=True)

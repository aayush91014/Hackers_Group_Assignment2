
import itertools, math, csv, json, random
from collections import Counter
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED)

# Variable order is topological: W, D, O, A, L, E
states = {
    "W": ["Hot", "Mild", "Cold"],
    "D": ["Weekday", "Weekend"],
    "O": ["High", "Low"],
    "A": ["On", "Off"],
    "L": ["Heavy", "Light"],
    "E": ["High", "Low"],
}
parents = {"W": [], "D": [], "O": ["D"], "A": ["W","O"], "L": ["O"], "E": ["A","L"]}

# Each entry is the probability of the first state in the child variable.
expert = {
    "W": {(): {"Hot":.50, "Mild":.30, "Cold":.20}},
    "D": {(): {"Weekday":.70, "Weekend":.30}},
    "O": {("Weekday",): {"High":.45, "Low":.55},
          ("Weekend",): {"High":.80, "Low":.20}},
    "A": {(w,o): {"On":p, "Off":1-p} for w,o,p in [
        ("Hot","High",.90),("Hot","Low",.60),("Mild","High",.40),
        ("Mild","Low",.15),("Cold","High",.10),("Cold","Low",.05)]},
    "L": {("High",): {"Heavy":.75,"Light":.25},
          ("Low",): {"Heavy":.35,"Light":.65}},
    "E": {(a,l): {"High":p,"Low":1-p} for a,l,p in [
        ("On","Heavy",.92),("On","Light",.68),("Off","Heavy",.55),("Off","Light",.12)]},
}
queries = [
    {"E":"High"},
    {"E":"High","W":"Hot"},
    {"E":"High","D":"Weekend"},
    {"E":"High","W":"Cold","O":"High"},
    {"W":"Hot","E":"High"},
    {"A":"On","E":"High"},
    {"A":"On","E":"High","L":"Heavy"},
]
q_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7"]

def joint_prob(row, cpts):
    pr = 1.0
    for v in states:
        key = tuple(row[p] for p in parents[v])
        pr *= cpts[v][key][row[v]]
    return pr

def infer(evidence, cpts):
    numerator = denominator = 0.0
    for vals in itertools.product(*(states[v] for v in states)):
        row = dict(zip(states, vals))
        if all(row[k] == val for k,val in evidence.items()):
            p = joint_prob(row,cpts)
            denominator += p
            if "E" in evidence and evidence["E"] == "High":
                # Qs whose target is W/A are identified by evidence below
                pass
            numerator += p
    # The queried variable is the first key in each query, and its target is encoded separately.
    return numerator, denominator

def query_probability(target_var, target_value, evidence, cpts):
    num = den = 0.0
    for vals in itertools.product(*(states[v] for v in states)):
        row = dict(zip(states, vals))
        if all(row[k] == val for k,val in evidence.items()):
            p = joint_prob(row,cpts); den += p
            if row[target_var] == target_value: num += p
    return num/den if den else float("nan")

q_specs = [
    ("E","High",{}),
    ("E","High",{"W":"Hot"}),
    ("E","High",{"D":"Weekend"}),
    ("E","High",{"W":"Cold","O":"High"}),
    ("W","Hot",{"E":"High"}),
    ("A","On",{"E":"High"}),
    ("A","On",{"E":"High","L":"Heavy"}),
]
def run_queries(cpts):
    return [query_probability(*s,cpts) for s in q_specs]

def validate(cpts):
    checks=[]
    for v, table in cpts.items():
        for cfg,dist in table.items():
            total=sum(dist.values())
            checks.append((v,cfg,total,abs(total-1)<1e-10))
    return checks

def sample_one(rng, cpts):
    row={}
    for v in states:
        cfg=tuple(row[p] for p in parents[v])
        probs=cpts[v][cfg]
        r=rng.random(); acc=0
        for value,p in probs.items():
            acc += p
            if r <= acc:
                row[v]=value; break
    return row

def generate_data(n, seed):
    rng=random.Random(seed)
    return [sample_one(rng,expert) for _ in range(n)]

def learn(data, estimator):
    cpts={}
    ess=10.0
    for v in states:
        configs=list(expert[v].keys())
        cpts[v]={}
        for cfg in configs:
            subset=[r for r in data if tuple(r[p] for p in parents[v])==cfg]
            counts={s:sum(r[v]==s for r in subset) for s in states[v]}
            k=len(states[v]); N=len(subset)
            if estimator=="MLE":
                if N==0:
                    probs={s:1/k for s in states[v]}
                else:
                    probs={s:counts[s]/N for s in states[v]}
            else:
                # BDeu: uniform Dirichlet prior; alpha_ijk = ESS/(q*r)
                alpha=ess/(len(configs)*k)
                probs={s:(counts[s]+alpha)/(N+ess/len(configs)) for s in states[v]}
            cpts[v][cfg]=probs
    return cpts

def write_csv(path, rows, headers):
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(headers)
        for row in rows: w.writerow(row)

def main():
    print("PART A: EXPERT BAYESIAN NETWORK")
    checks=validate(expert)
    print("CPT rows checked:",len(checks)," all sum to 1:",all(x[3] for x in checks))
    print("Expert Q1-Q7:",[round(x,6) for x in run_queries(expert)])
    # Q1 manual marginalization over A,L.
    q1=0
    for w,pw in expert["W"][()].items():
        for d,pd in expert["D"][()].items():
            for o,po in expert["O"][(d,)].items():
                for a,pa in expert["A"][(w,o)].items():
                    for l,pl in expert["L"][(o,)].items():
                        q1 += pw*pd*po*pa*pl*expert["E"][(a,l)]["High"]
    print("Q1 manual summation:",round(q1,10))
    print("Q1 hand-work structure: sum_w sum_d sum_o sum_a sum_l P(w)P(d)P(o|d)P(a|w,o)P(l|o)P(E=High|a,l)")
    print("  = sum over all 3x2x2x2x2 parent-state combinations; total =",round(q1,10))
    print("Explaining away: Q6 =",round(run_queries(expert)[5],6),
          " Q7 =",round(run_queries(expert)[6],6))
    print("\\nPART B: CONDITIONAL INDEPENDENCE")
    # W and D independent marginally; dependent after conditioning on E (collider path W->A->E<-L<-O<-D).
    # W and L are independent given O because paths through O are blocked and no open alternative.
    p_w_hot_e=run_queries(expert)[4]
    p_w_hot_e_weekend=query_probability("W","Hot",{"E":"High","D":"Weekend"},expert)
    p_w_hot=query_probability("W","Hot",{},expert)
    p_w_hot_weekend=query_probability("W","Hot",{"D":"Weekend"},expert)
    print("W independent D:",round(p_w_hot,6),round(p_w_hot_weekend,6))
    print("W independent D | E? compare:",round(p_w_hot_e,6),round(p_w_hot_e_weekend,6))
    for occ in ["High","Low"]:
        p0=query_probability("W","Hot",{"O":occ},expert)
        p1=query_probability("W","Hot",{"O":occ,"L":"Heavy"},expert)
        p2=query_probability("W","Hot",{"O":occ,"L":"Light"},expert)
        print(f"W independent L | O={occ}: P(Hot|O)={p0:.6f}, P(Hot|O,Heavy)={p1:.6f}, P(Hot|O,Light)={p2:.6f}")
    print("\\nPART C/D: DATA AND PARAMETER LEARNING")
    all_results={}
    for n in [500,5000,20000]:
        data=generate_data(n,SEED+n)
        freq=Counter(r["W"] for r in data)
        combo=Counter((r["W"],r["O"]) for r in data)
        print(f"n={n}; weather frequencies={dict(freq)}")
        print("Weather,Occupancy counts:",{str(k):v for k,v in combo.items()})
        for est in ["MLE","Bayesian"]:
            model=learn(data,est)
            vals=run_queries(model)
            diffs=[abs(a-b) for a,b in zip(vals,run_queries(expert))]
            all_results[(n,est)]=(vals,diffs)
            print(est,"Q1-Q7:",[round(x,6) for x in vals],
                  "mean abs diff:",round(sum(diffs)/7,6))
        # save AC CPT comparison
        with open(f"outputs/ac_cpt_{n}.txt","w") as f:
            f.write("Expert AC CPT\\n")
            for cfg,d in expert["A"].items(): f.write(f"{cfg}: {d}\\n")
            for est in ["MLE","Bayesian"]:
                f.write(f"\\n{est} AC CPT\\n")
                for cfg,d in learn(data,est)["A"].items(): f.write(f"{cfg}: {d}\\n")
        write_csv(f"outputs/weather_occupancy_{n}.csv",
                  [(w,o,combo[(w,o)]) for w in states["W"] for o in states["O"]],
                  ["Weather","Occupancy","Count"])
    # Comparative tables
    for n in [500,5000,20000]:
        with open(f"outputs/comparison_{n}.csv","w",newline="") as f:
            wr=csv.writer(f); wr.writerow(["Query","Expert","MLE","Bayesian","AbsDiff_MLE","AbsDiff_Bayesian"])
            exp=run_queries(expert); m,dm=all_results[(n,"MLE")]; b,db=all_results[(n,"Bayesian")]
            for i in range(7): wr.writerow([q_names[i],exp[i],m[i],b[i],dm[i],db[i]])
    sizes=[500,5000,20000]
    for est in ["MLE","Bayesian"]:
        means=[sum(all_results[(n,est)][1])/7 for n in sizes]
        plt.plot(sizes,means,marker="o",label=est)
    plt.xscale("log"); plt.xlabel("Dataset size"); plt.ylabel("Mean absolute difference (Q1-Q7)")
    plt.title("Parameter-learning error vs dataset size"); plt.legend(); plt.grid(True,alpha=.3)
    plt.tight_layout(); plt.savefig("figures/learning_error.png",dpi=160); plt.close()
    print("\\nLargest-error query for n=500 (MLE):",
          q_names[max(range(7),key=lambda i:all_results[(500,"MLE")][1][i])])
    print("Bayesian estimation usually stabilizes small-sample CPTs through its Dirichlet prior.")
    print("NOTE: all data are synthetic samples from the expert network; seed =",SEED)
if __name__=="__main__": main()

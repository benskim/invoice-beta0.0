## load po, invoice files
po_lines= [
  {
    "id": "PO1",
    "desc": "B-RACK 600W*800D*2000H SECC 48V P/C RAL9005",
    "features": {
      "product_family": "STR", #// Structure -> STR
      "critical": {
        "core_spec": "Rack Frame",
        "dim": "600*800*2000",
        "mat": "SECC",
        "volt": "48V"
      },
      "auxiliary": {
        "finish": "P/C", #// Powder Coated
        "color": "RAL9005"
      }
    },
    "qty": 10,
    "unit_price": 1200,
    "amt": 12000
  },
  {
    "id": "PO2",
    "desc": "HVAC CLU 220VAC 5kW R134a IND",
    "features": {
      "product_family": "HVAC", #// Cooling -> HVAC(Heating, Ventilation, and Air Conditioning)
      "critical": {
        "core_spec": "Cooling Unit",
        "volt": "220VAC",
        "pwr": "5kW"
      },
      "auxiliary": {
        "refrig": "R134a",
        "grade": "IND" #// Industrial
      }
    },
    "qty": 4,
    "unit_price": 2500,
    "amt": 10000
  },
  {
    "id": "PO3",
    "desc": "BMS MOD V2 RJ45 CAN B-LED",
    "features": {
      "product_family": "CTRL", #// Control -> CTRL
      "critical": {
        "core_spec": "BMS Module",
        "if": "RJ45", #// Interface -> if
        "prot": "CAN" #// Protocol -> prot
      },
      "auxiliary": {
        "ver": "V2",
        "ind": "B-LED" #// Indicator -> ind
      }
    },
    "qty": 20,
    "unit_price": 450,
    "amt": 9000
  },
  {
    "id": "PO4",
    "desc": "Busbar Cu M8 300L N/P UL",
    "features": {
      "product_family": "ELEC",
      "critical": {
        "core_spec": "Busbar",
        "mat": "Cu", #// Copper -> Cu
        "term": "M8",
        "len": "300L" #// Length -> L
      },
      "auxiliary": {
        "plat": "N/P", #// Nickel Plated -> N/P
        "cert": "UL"
      }
    },
    "qty": 100,
    "unit_price": 15,
    "amt": 1500
  }
]

invoice_lines=[
  {
    "id": "INV1",
    "po_ref": "PO2",
    "desc": "IND CLU 48V 5kW R134a ECO",
    "features": {
      "product_family": "HVAC",
      "critical": {
        "core_spec": "Cooling Unit",
        "volt": "48V", #// PO(220VAC)와 불일치
        "pwr": "5kW"
      },
      "auxiliary": {
        "refrig": "R134a",
        "tag": "ECO"
      }
    },
    "qty": 10,
    "unit_price": 1200,
    "amt": 12000
  },
  {
    "id": "INV2",
    "po_ref": "PO1",
    "desc": "B-RACK 600*800*2000 SUS304 110V M-BLK",
    "features": {
      "product_family": "STR",
      "critical": {
        "core_spec": "Rack Frame",
        "mat": "SUS304", #// PO(SECC)와 불일치
        "volt": "110V",   #// PO(48V)와 불일치
        "dim": "600*800*2000"
      },
      "auxiliary": {
        "finish": "M-BLK" #// Matt Black
      }
    },
    "qty": 10,
    "unit_price": 1250,
    "amt": 12500
  },
  {
    "id": "INV3",
    "po_ref": "PO4",
    "desc": "Busbar Cu M6 250L S/P RoHS",
    "features": {
      "product_family": "ELEC",
      "critical": {
        "core_spec": "Busbar",
        "mat": "Cu",
        "term": "M6",   #// PO(M8)와 불일치
        "len": "250L"   #// PO(300L)와 불일치
      },
      "auxiliary": {
        "plat": "S/P", #// Silver Plated -> S/P
        "cert": "RoHS"
      }
    },
    "qty": 100,
    "unit_price": 15,
    "amt": 1500
  }
]



from collections import defaultdict
import re
from rapidfuzz import fuzz


# Product family별 critical features 정의 (severity level별)
FEATURE_CRITICALITY = {
    "STR": {  # Structure
        "L1": ["core_spec"],  # 다른 제품
        "L2": ["mat", "volt"],  # 재질, 전압
        "L3": ["dim", "finish"],  # 치수, 도장
    },
    "HVAC": {  # Cooling/HVAC
        "L1": ["core_spec"],
        "L2": ["volt", "pwr"],  # 전압, 전력
        "L3": ["refrig", "grade"],  # 냉매, 등급
    },
    "CTRL": {  # Control
        "L1": ["core_spec"],
        "L2": ["volt", "prot"],  # 전압, 프로토콜
        "L3": ["if", "pwr"],  # 인터페이스, 전력
    },
    "ELC": {  # Electrical
        "L1": ["core_spec"],
        "L2": ["mat", "terminal"],  # 재질, 단자
        "L3": ["dim"],  # 치수
    },
    "BTR": {  # Battery
        "L1": ["core_spec"],
        "L2": ["volt", "capacity"],  # 전압, 용량
        "L3": ["mat"],  # 재질
    },
}


def normalize_text(text):
    # next version
    # Unit Normalization (단위 정규화): 인보이스에 30cm로 적혀 있어도 L5의 300mm와 동일값으로 인식하도록 
    # 변환 로직을 갖춰야 합니다.
    # Material Alias (재질 별칭): SECC와 Steel 혹은 Copper와 Cu를 동일한 속성값으로 매핑하여 
    # 텍스트 불일치를 해결합니다.
    return text.strip().lower().replace("  ", "")



# def extract_features(desc):
#     # 향후 dictionary, regex-map으로 해결
#     return {
#         "category": extract_category(desc),
#         # core specifications conflict - material, voltage, power
#         "material": extract_material(desc),
#         "voltage": extract_voltage(desc),
#         # key identifier conflict - model, dimension, interface, capacity
#         "model": extract_model(desc), #version
#         # "interface": extract_interface(desc), # network
#         # "dimension": extract_dimension(desc),
#         # "capacity": extract_capacity(desc),
#     }


# build po index db (changable by company)
def build_po_index(po_lines):
    # return
    # { "battery rack" : [ "stainless" : [ {po_line1}, {po_line2} ]
    #                      , "steel" : [ {po_line3} ] ] }
    # }
    index = defaultdict(lambda: defaultdict(dict))

    # extract features for each PO line and build index by category
    for po_line in po_lines:
        po_line["desc"] = normalize_text(po_line["desc"])

        # w/o LLM version
        # features = extract_features(po_line["desc"])
        # po_line["features"] = features
        
        # w/ LLM version
        features = po_line["features"]

        # name --> key value

        product_family = normalize_text(features.get("product_family", "unknown"))
        core_spec = normalize_text(features.get("core_spec", "unknown"))
        # voltage = features.get("voltage", "unknown")
        index[product_family][core_spec][po_line["id"]] = po_line
    return index

def retrieve_candidates(invoice_line, po_index):
    # return
    # [ {po_line1}, {po_line2} ]
   
    invoice_line["desc"] = normalize_text(invoice_line["desc"])
    
    # w/o LLM version
    # features = extract_features(invoice_line["desc"])
    
    # w/ LLM version
    features = invoice_line["features"]
    product_family = normalize_text(features.get("product_family", "unknown"))
    core_spec = normalize_text(features.get("core_spec", "unknown")) # diff norm by family***************
    # voltage = features.get("voltage", "unknown")

    candidates = []

    # Level 1
    if product_family not in po_index:
        return candidates

    # Level 2
    if core_spec not in po_index[product_family]:
        # fallback:
        # core_spec 무시하고 category 전체 사용
        for items in po_index[product_family].values():
            candidates.extend(list(items.values()))
        return candidates

    # Level 3
    candidates = list(po_index[product_family][core_spec].values())
    return candidates


def tokenize(text: str):
    """
    Example:
    Samsung SSD 1TB 10ea
    ->
    ['samsung', 'ssd', '1tb', '10ea']
    """
    # text = normalize(text)
    tokens = re.findall(r"[a-zA-Z0-9\.]+", text)
    return tokens

def extract_numbers(tokens):
    """    Extract numeric-ish tokens
    Example:
    ['ssd', '1tb', '10ea']
    ->
    ['1tb', '10ea']
    """
    nums = []
    for t in tokens:
        if re.search(r"\d", t):
            nums.append(t)
    return nums

def coverage(tokens1, tokens2):
    """
    How much of PO is covered by invoice
    invoice covers PO 얼마나 많이 포함?
    """
    s1 = set(tokens1)
    s2 = set(tokens2)
    if not s2:
        return 0.0
    inter = len(s1 & s2)
    return inter / len(s2)

def numeric_overlap(nums1, nums2):
    """    
    Numeric token overlap
    Example:   
    ['1tb', '10ea']    vs    ['1tb', '12ea']
    -> 0.5
    """
    s1 = set(nums1)
    s2 = set(nums2)
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    inter = len(s1 & s2)
    union = len(s1 | s2)
    return inter / union

# def token_frequency_similarity(tokens1, tokens2):
#     """
#     Counter-based similarity : boundles/qunatity similarity
#     Helps repeated token cases
#     """
#     c1 = Counter(tokens1)
#     c2 = Counter(tokens2)
#     common = 0
#     for k in c1:
#         common += min(c1[k], c2.get(k, 0))
#     total = max(sum(c1.values()), sum(c2.values()))
#     if total == 0:
#         return 0.0
#     return common / total

def format_similarity(text1, text2):
    """
    Fuzz token sort ratio as similarity score
    """
    return fuzz.token_sort_ratio(text1, text2) / 100

def calculate_similarity(inv_text, po_text):

    # 1. text similarity
    coverage_score = coverage(tokenize(inv_text), tokenize(po_text))
    fuzzy_score = format_similarity(inv_text, po_text)

    # 2. numeric similarity
    numeric_score = numeric_overlap(extract_numbers(tokenize(inv_text)), extract_numbers(tokenize(po_text)))

    # -------------------------------
    # weighted final score
    # -------------------------------
    final_score = (
        0.30 * coverage_score +
        0.30 * fuzzy_score +
        0.40 * numeric_score 
    )

    return {
        "final_score": round(final_score, 4),
        "detail": {
            "coverage": round(coverage_score, 4),
            "fuzzy": round(fuzzy_score, 4),
            "numeric": round(numeric_score, 4),  
        }
    }


# def classify_severity_score(severity_score):
#     # severity_score 기반으로 severity 결정
#     if severity_score <= -3:
#         return "L1"
#     elif severity_score <= -2:
#         return "L2"
#     elif severity_score == -1:
#         return "L3"
#     else:
#         return "L4"

def classify_severity_reason(severity_reason):
    if severity_reason:
        reasons = severity_reason.strip(', ').split(', ')
        # L1: critical features - product family, core spec (different product)
        if "product_family" in reasons or "core_spec" in reasons:
            return "L1"
        # L2: critical specs - material, voltage, power (specification conflict)
        elif "mat" in reasons or "volt" in reasons or "pwr" in reasons or \
             "material" in reasons or "voltage" in reasons or "power" in reasons:
            return "L2"
        # L3: key specs - dimension, interface, protocol (model conflict)
        elif "dim" in reasons or "if" in reasons or "prot" in reasons or \
             "dimension" in reasons or "interface" in reasons or "model" in reasons or \
             "terminal" in reasons or "capacity" in reasons:
            return "L3" 
        # L4: auxiliary specs - color, finish, grade
        elif "color" in reasons or "finish" in reasons or "grade" in reasons or "refrig" in reasons:
            return "L4"
    return "L5"  # No significant issues


def classify_severity_by_similarity(product_family, lowest_similarity, num_mismatches, total_critical_features):
    """
    Similarity 기반 severity 분류 (제품군 고려)
    - lowest_similarity: 가장 낮은 feature similarity score
    - num_mismatches: mismatch된 feature 수
    - total_critical_features: critical feature 총 개수
    """
    if product_family not in FEATURE_CRITICALITY:
        product_family = "STR"  # default
    
    # mismatch 비율
    mismatch_ratio = num_mismatches / max(total_critical_features, 1)
    
    # critical feature 다 missing/mismatch → L1
    if mismatch_ratio > 0.5 and "core_spec" in [f for level in FEATURE_CRITICALITY[product_family].values() for f in level]:
        return "L1"
    
    # similarity 기반 분류 (낮을수록 심각)
    if lowest_similarity < 0.5:
        return "L2"  # 심각한 차이
    elif lowest_similarity < 0.7:
        return "L3"  # 중간 차이
    elif lowest_similarity < 0.9:
        return "L4"  # 미미한 차이
    else:
        return "L5"  # 무시할 수 있는 수준   

# def classify_severity(pof,invf):
    # feature importance 기반으로 severity 결정
    # 예시: specification conflict > quantity mismatch
    # if pof["category"] != invf["category"]:
    #     return "L1"
    # elif pof["material"] != invf["material"]:
    #     return "L2"
    # elif pof["voltage"] != invf["voltage"]:
    #     return "L3"
    # else:
    #     return "L4" 

def predict_decision(score, severity):
    # score + severity 기반으로 승인/거절 결정
    if severity in ["L1", "L2"]:
        return "Reject"
    elif severity in ["L3", "L4"] and score < 0.7:
        return "Review"
    else:
        return "Approve"
    

# workflow
#upload
#parse+extract
#indexing
po_index_db = build_po_index(po_lines)

for line in invoice_lines:
    # print(line['desc']) - debug
    # print(line['features']) #- debug
    #retrieve candidates for each invoice line
    line["candidates"] = retrieve_candidates(line, po_index_db)
    # print(line["candidates"]) #- debug

    for po_item in line["candidates"]:
        po_item["severity_score"] = 0 #setdefault하면 중복 저장됨.
        po_item["score"] = 0
        po_item["severity_reason"] = ""
        po_item["similarities"] = {}  # feature별 similarity score 저장
        po_item["num_mismatches"] = 0  # mismatch feature 수

    # 인보이스에서 추출된 유효한 피처만 추출
    valid_crt_features = {k: v for k, v in line['features']['critical'].items() if v is not None} #  L2L3
    valid_aux_features = {k: v for k, v in line['features']['auxiliary'].items() if v is not None} # L3L4
    #// DESC FORAMT # L5

    # feature 기반 후보군 평가 및 점수 계산 --> feature weight map 필요[ver3]
    for feature_name, inv_value in valid_crt_features.items():
        for po_item in line["candidates"]:
            po_c_value = po_item['features']['critical'].get(feature_name) # rule+score
            po_a_value = po_item['features']['auxiliary'].get(feature_name) # score
            
            if po_c_value is not None:
                print("yes : " , po_c_value ," === ?",inv_value) #- debug
                # 둘 다 값이 있을 때만 본격적인 '유사도 계산' 혹은 '단순 비교' 수행
    
                # feature comparision
                sim_result =  calculate_similarity(inv_value, po_c_value)["final_score"]
                po_item["similarities"][feature_name] = sim_result  # similarity 저장
                po_item["score"] += sim_result *0.2 #feature별 가중치 예시(소수점 float)
                if sim_result < 0.8:
                    po_item['severity_score'] = po_item.get('severity_score', 0) - 1
                    po_item['severity_reason'] = po_item.get('severity_reason', '') + feature_name + ', '
                    po_item['num_mismatches'] += 1  # mismatch 수 증가
                # desc comparison
                # po_item["score"] = calculate_similarity(line['desc'], po_item['desc'])["final_score"]

            else:
                # PO에 정보가 없는 경우: 심각한 탈락!
                # 일치도에 영향을 주지 않거나 감점 처리
                po_item['severity_score'] = po_item.get('severity_score', 0) - 1
                po_item['severity_reason'] = po_item.get('severity_reason', '') + feature_name + ', '
                po_item['similarities'][feature_name] = 0.0  # PO에 정보 없음 = 0.0
                po_item['num_mismatches'] += 1  # mismatch 수 증가
                print("no : ",inv_value, "=== ?",po_c_value) #- debug
    
    # qty, unit price 비교 - numeric mismatch는 별도 관리 (input : should be normalized beforehand)
    # feature loop 밖에서 한 번만 체크
    for po_item in line["candidates"]:
        if qty_diff := abs(line['qty'] - po_item['qty']):
            po_item['severity_reason'] = po_item.get('severity_reason', '') + "quantity_diff,"
            print("quantity mismatch : ",line['qty'], "vs", po_item['qty']) #- debug
            # if line['qty'] > po_item['qty']:
            #     po_item['severity_score'] = po_item.get('severity_score', 0) - 1
            # else: #line['qty'] < po_item['qty']:
            #     po_item['severity_score'] = po_item.get('severity_score', 0) - 0.5
                
        if unit_price_diff := abs(line['unit_price'] - po_item['unit_price']):
            po_item['severity_reason'] = po_item.get('severity_reason', '') + "unit_price_diff,"
            print("unit price mismatch : ",line['unit_price'], "vs", po_item['unit_price']) #- debug
            # if line['unit_price'] > po_item['unit_price']:
            #     po_item['severity_score'] = po_item.get('severity_score', 0) - 1    
            # else:
            #     po_item['severity_score'] = po_item.get('severity_score', 0) - 0.5
    
    # rank candidates by score and select best match
    line["candidates"].sort(
        key=lambda x: (x.get("severity_score", 0), x.get("score", 0)),
        reverse=True,
    )
    line["best_match"] = line["candidates"][0] if line["candidates"] else None  
    # print(line["candidates"]) - debug

    # classifiy serverity : L1~L5 based on similarity and criticality
    best_match = line["best_match"]
    best_severity_score = best_match.get("severity_score", 0) if best_match else 0
    best_score = best_match.get("score", 0) if best_match else 0
    best_severity_reason = best_match.get("severity_reason", "") if best_match else ""
    
    if best_match:
        # product family 추출
        product_family = best_match['features'].get('product_family', 'STR')
        
        # lowest similarity 계산
        similarities = best_match.get("similarities", {})
        lowest_similarity = min(similarities.values()) if similarities else 1.0
        
        # critical feature 개수
        criticality = FEATURE_CRITICALITY.get(product_family, FEATURE_CRITICALITY["STR"])
        total_critical_features = len([f for level in criticality.values() for f in level])
        num_mismatches = best_match.get('num_mismatches', 0)
        
        # similarity 기반 severity 분류 (우선)
        line["severity"] = classify_severity_by_similarity(
            product_family, lowest_similarity, num_mismatches, total_critical_features
        )
    else:
        line["severity"] = "L5"
    
    line["decision"] = predict_decision(best_score, line["severity"])


# """
# Review Completed

# Accepted: 124
# Rejected: 18
# Needs Manual Review: 7

# Auto-match confidence updated
# 3 new mismatch patterns detected

# >> The following patterns will improve future matching:

# ✓ learned alias:
#   "BOLT M8" ≈ "M8 BOLT"

# ✓ learned rejection:
#   "6204-ZZ" ≠ "6204-2RS"

# ✓ detected high-risk mismatch:
#   qty difference > 40%
# """

    score_text = f"{best_score:.4f}" if best_match else "N/A"
    print(
        f"severity_reason : {best_severity_reason}",
        f"Invoice Line: {line['id']}, Best Match PO Line: {best_match['id'] if best_match else 'None'}, "
        f"Score: {score_text}, Severity: {line['severity']}, Decision: {line['decision']}"
    )

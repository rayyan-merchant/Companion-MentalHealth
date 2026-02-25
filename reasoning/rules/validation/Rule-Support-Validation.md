# Rule-Support Validation Document

## Purpose
This document validates that all properties required by SWRL rules exist in the ontology and identifies any gaps where rules may invent semantics not in the ontology.

## Properties Used in SWRL Rules

### Object Properties Used in Rules

| Property | Used in Rules | Defined in Ontology | Status |
|----------|---------------|-------------------|---------|
| [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84) | Yes | ✓ | Validated |
| [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139) | Yes | ✓ | Validated |
| [triggeredBy](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L233-L237) | Yes | ✓ | Validated |
| [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106) | Yes | ✓ | Validated |

### Data Properties Used in Rules

| Property | Used in Rules | Defined in Ontology | Status |
|----------|---------------|-------------------|---------|
| (No data properties used in SWRL rules) | N/A | N/A | N/A |

## SWRL Rule to Property Mapping

### Academic Stress & Anxiety Rules
- **R_ACS_01a**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Stress](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1143-L1146), [triggeredBy](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L233-L237), [Exam_Pressure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L690-L694)
- **R_ACS_01b**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Stress](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1143-L1146), [triggeredBy](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L233-L237), [Academic_Workload](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L473-L477)
- **R_ANX_01**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Stress](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1143-L1146), [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139), [Insomnia](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L820-L824), [triggeredBy](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L233-L237), [Exam_Pressure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L690-L694)
- **R_ANX_02**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Anxiety](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L489-L499), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)

### Burnout & Chronic Stress Rules
- **R_BRN_01**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Emotional_Overwhelm](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L639-L644), [triggeredBy](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L233-L237), [Academic_Workload](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L473-L477), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)
- **R_BRN_02**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Stress](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1143-L1146), [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139), [Fatigue](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L730-L734), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)

### Panic & Acute Stress Rules
- **R_PAN_01**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Anxiety](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L489-L499), [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139), [Rapid_Heart_Rate](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L990-L994), [Breathing_Difficulty](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L551-L555)

### Depressive Spectrum Rules
- **R_DEP_01**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [SocialISolationRisk](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1102-L1106), [experiencesEmotion](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L79-L84), [Emotional_Overwhelm](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L639-L644), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)
- **R_DEP_02**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139), [Fatigue](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L730-L734), [hasSymptom](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L134-L139), [Insomnia](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L820-L824), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [SocialISolationRisk](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1102-L1106)

### Risk-Level Attribution Rules
- **R_RISK_01a**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [AnxietyRisk](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L503-L507), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)
- **R_RISK_01b**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [BurnoutRisk](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L559-L563), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)
- **R_RISK_02**: Uses [Student](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1167-L1170), [PanicRisk](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L918-L922), [hasRiskFactor](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L101-L106), [RepeatedStressExposure](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1006-L1010)

## Gap Analysis

### ✅ Validated Properties
All properties used in SWRL rules are defined in the ontology and no rule invents semantics not in the ontology.

### ⚠️ Conceptual Gaps Identified

1. **Persistence Tracking Properties**
   - **Gap**: The conceptual design (context.md line 256) mentions a `persistsFor` property with a `swrlb:greaterThan(?d, 7)` condition to check if something persists for more than 7 days
   - **Status**: This property exists in conceptual documentation but is NOT implemented in the actual SWRL rules
   - **Impact**: The current rules don't implement persistence-based reasoning as described in the conceptual model

2. **Confidence-Related Properties**
   - **Gap**: The ontology defines a [confidenceScore](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L265-L275) data property but it is not used in any SWRL rules
   - **Status**: Property exists in ontology but not utilized in reasoning
   - **Impact**: The system may extract confidence scores but doesn't use them in rule-based reasoning

3. **Severity Ordering Properties**
   - **Gap**: The ontology defines [hasSeverity](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L122-L128), [severityScore](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L428-L434), and severity classes ([Mild](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L892-L898), [Moderate](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L902-L906), [Severe](file:///c%3A/Users/Me/Downloads/Mental%20Health%20KRR/Mental%20Health%20KRR/ontology/mental_health.owl#L1054-L1058)) but these are not used in SWRL rules
   - **Status**: Properties exist in ontology but not utilized in reasoning
   - **Impact**: Severity levels are defined but not used in rule-based reasoning

## Validation Summary

✅ **All properties used in SWRL rules are defined in the ontology** - No rule invents semantics not in the ontology

⚠️ **Conceptual gaps exist** where the design documentation mentions properties that are not implemented in the actual rules

## Recommendations

1. **Implement Persistence Tracking**: Add the `persistsFor` property and associated rules to handle temporal aspects of mental health conditions
2. **Utilize Confidence Properties**: Modify SWRL rules to incorporate confidence scores in reasoning when available
3. **Integrate Severity Properties**: Update rules to use severity levels in decision-making processes
4. **Align Implementation with Design**: Bridge the gap between conceptual design and actual implementation

## Conclusion

The SWRL rules are properly aligned with the ontology in terms of property usage - no rule uses properties that are not defined in the ontology. However, there are conceptual features described in the documentation that are not implemented in the actual rules, creating potential gaps in functionality.
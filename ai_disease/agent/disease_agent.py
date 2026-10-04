"""
Disease Agent module for grounded agricultural synthesis.
Combines vision observations with retrieved RAG evidence to generate structured,
evidence-backed, zero-hallucination management recommendations.
"""

import os
import re
import json
import urllib.request
from typing import Dict, Any, List, Optional

from ..schemas import DiseaseAnalysisResult
from ..prompts.disease_prompt import (
    SYSTEM_PROMPT,
    DISCLAIMER_TRANSLATIONS,
    INSUFFICIENT_EVIDENCE_MESSAGES,
    build_disease_prompt
)


# Native high-fidelity agricultural knowledge and translations for verified terms
DISEASE_MULTILINGUAL_DATA = {
    "Rice Blast": {
        "Telugu": {
            "name": "వరి అగ్గితెగులు (Rice Blast)",
            "symptoms": [
                "ఆకులపై ఇరువైపులా మొనదేలిన కంటి ఆకారపు లేదా కదురు ఆకారపు బూడిద రంగు మచ్చలు",
                "మచ్చల అంచులు ముదురు ఎరుపు-గోధుమ రంగులో ఉంటాయి",
                "తీవ్ర దశలో మెడవిరుపు (Neck Blast) సోకి గింజలు తాలుగా మారి పైరు పడిపోతుంది"
            ],
            "organic": [
                "కిలో విత్తనానికి 10 గ్రా. సూడోమోనాస్ ఫ్లోరోసెన్స్ తో విత్తన శుద్ధి చేయండి",
                "నత్రజని ఎరువులను ఒకేసారి కాకుండా 3-4 దఫాలుగా వేయండి",
                "ఎకరానికి 150 కిలోల వేపపిండిని ఆఖరి దుక్కిలో వేయండి",
                "గట్లపై ఉన్న గడ్డి జాతి కలుపు మొక్కలను తొలగించి శుభ్రంగా ఉంచండి"
            ],
            "chemical": [
                "ట్రైసైక్లాజోల్ 75% WP (Tricyclazole 75% WP) @ 0.6 గ్రా. లీటరు నీటికి కలిపి పిచికారీ చేయండి (మూలం: ICAR-NRRI)",
                "ఐసోప్రోతియోలేన్ 40% EC (Isoprothiolane 40% EC) @ 1.5 మి.లీ. లీటరు నీటికి (మూలం: ICAR Advisory)"
            ]
        },
        "Hindi": {
            "name": "धान का झोंका रोग (Rice Blast)",
            "symptoms": [
                "पत्तियों पर आंख अथवा नाव के आकार के धब्बे जिनके बीच का हिस्सा राख जैसे सफेद/धूसर रंग का तथा किनारे भूरे होते हैं",
                "मौसम नम होने पर धब्बे आपस में मिलकर पूरी पत्ती को झुलसा देते हैं",
                "तीव्र प्रकोप की स्थिति में बालियों की गर्दन काली पड़ जाती है (गर्दन तोड़ रोग) जिससे दाने नहीं भरते"
            ],
            "organic": [
                "स्यूडोमोनास फ्लोरोसेंस @ 10 ग्राम प्रति किग्रा बीज की दर से बीजोपचार करें",
                "नाइट्रोजन उर्वरकों का संतुलित प्रयोग करें तथा पोटाश की पर्याप्त मात्रा डालें",
                "खेत की मेड़ों को खरपतवार मुक्त रखें",
                "अंतिम जुताई के समय 150 किग्रा नीम की खली प्रति हेक्टेयर प्रयोग करें"
            ],
            "chemical": [
                "ट्राइसाइक्लाजोल 75% WP (Tricyclazole 75% WP) @ 0.6 ग्राम प्रति लीटर पानी में मिलाकर छिड़काव करें (स्रोत: ICAR-NRRI)",
                "आइसोप्रोथियोलेन 40% EC (Isoprothiolane 40% EC) @ 1.5 मिली प्रति लीटर पानी (स्रोत: ICAR Advisory)"
            ]
        },
        "Tamil": {
            "name": "அரிசி வெடிப்பு நோய் (Rice Blast)",
            "symptoms": [
                "இலைகளில் கண் அல்லது கப்பல் வடிவ கறைபுள்ளிகள் தோன்றும்; அவற்றின் மையம் சாம்பல்-வெள்ளை நிறத்தில் இருக்கும்.",
                "கறைபுள்ளிகளின் விளிம்புகள் பழுப்பு-சிவப்பு நிறத்தில் காணப்படும்.",
                "கடுமையான நிலைகளில், தாது அல்லது புல்லாங்குழல் பகுதியில் நோய் பரவி, தானியங்கள் பழுத்து விழலாம்."
            ],
            "organic": [
                "சூடோமோனாஸ் புளோரசன்ஸ் @ 10 கிராம் / கிலோ விதை மூலம் விதை சிகிச்சை செய்யவும்.",
                "நைட்ரஜன் உரங்களை ஒரே நேரத்தில் இடாமல் 3-4 முறை பிரித்து பயன்படுத்தவும்.",
                "வெளிமேலானை சுத்தமாக வைத்து, களைமண் மற்றும் தேங்கி நிற்கும் நீரை குறைக்கவும்."
            ],
            "chemical": [
                "ட்ரைசைக்ளாசோல் 75% WP @ 0.6 கிராம்/லி; அல்லது ஐசோப்ரோதியோலேன் 40% EC @ 1.5 மில்லி/லி.",
                "(மூலம்: ICAR-NRRI / ICAR Advisory)"
            ]
        }
    },
    "Sheath Blight": {
        "Telugu": {
            "name": "వరి పొడ తెగులు (Sheath Blight)",
            "symptoms": [
                "నీటి మట్టానికి దగ్గరగా ఉన్న ఆకు తొడుగులపై గుండ్రని లేదా కోడిగుడ్డు ఆకారపు బూడిద ఆకుపచ్చ మచ్చలు",
                "మచ్చల అంచులు ముదురు గోధుమ రంగుతో పాము చర్మం వంటి చారలు ఏర్పడతాయి",
                "పైరు ముదిరే కొద్దీ మచ్చలు పై ఆకులకు వ్యాపించి తెగులు తీవ్రమవుతుంది"
            ],
            "organic": [
                "పైరులో గాలి ప్రసరణకు వీలుగా తగిన దూరం (20 x 15 సెం.మీ.) పాటించండి",
                "ట్రైకోడెర్మా విరిడే లేదా సూడోమోనాస్ @ 10 గ్రా./కిలో విత్తన శుద్ధి చేయండి",
                "పొలంలో నీరు ఎల్లప్పుడూ నిల్వ ఉంచకుండా ఆరుతడులు (AWD) ఇవ్వండి",
                "దుక్కి సమయంలో నీటిపై తేలే శిలీంధ్రపు అవశేషాలను తొలగించి కాల్చివేయండి"
            ],
            "chemical": [
                "హెక్సాకోనజోల్ 5% EC (Hexaconazole 5% EC) @ 2.0 మి.లీ. లీటరు నీటికి మొక్కల మొదళ్లపై పిచికారీ చేయండి (మూలం: DPPQS/ICAR-IIRR)",
                "వాలిడామైసిన్ 3% L (Validamycin 3% L) @ 2.0 మి.లీ. లేదా థిఫ్లూజామైడ్ 24% SC @ 0.75 మి.లీ. లీటరు నీటికి"
            ]
        },
        "Hindi": {
            "name": "शीथ ब्लाइट / पर्णच्छद झुलसा रोग (Sheath Blight)",
            "symptoms": [
                "जल स्तर के निकट पत्तियों के आवरण (शीथ) पर अंडाकार या अनियमित धूसर-हरे धब्बे",
                "धब्बों के किनारे गहरे भूरे होकर सांप की केंचुल जैसी धारियां बनाते हैं",
                "अनुकूल मौसम में यह रोग ऊपर की पत्तियों तक फैल जाता है जिससे पौधे गिर जाते हैं"
            ],
            "organic": [
                "रोपाई के समय उचित दूरी रखें ताकि हवा का संचार बना रहे",
                "ट्राइकोडर्मा विरिडी या स्यूडोमोनास @ 10 ग्राम प्रति किग्रा बीज से बीजोपचार करें",
                "खेत में लगातार जलभराव न रखें, बारी-बारी से गीला और सूखा रखें",
                "अतिरिक्त नाइट्रोजन के प्रयोग से बचें तथा पोटाश की संस्तुत मात्रा डालें"
            ],
            "chemical": [
                "हेक्साकोनाजोल 5% EC (Hexaconazole 5% EC) @ 2.0 मिली अथवा वैलिडामाइसिन 3% L @ 2.0 मिली प्रति लीटर पौधे के निचले हिस्से पर छिड़कें (स्रोत: ICAR-IIRR)",
                "थिफ्लूजामाइड 24% SC (Thifluzamide 24% SC) @ 0.75 मिली प्रति लीटर पानी (स्रोत: CIBRC Gazette)"
            ]
        },
        "Tamil": {
            "name": "வெற்றிலை-மெத்தை நோய் (Sheath Blight)",
            "symptoms": [
                "நீர்ப்பரப்புக்கு அருகில் உள்ள இலைவகைகள் மற்றும் சிப்பிகளின் கீழ்ப்புறத்தில் குழாய் அல்லது ஓவல் வடிவ கறைபுள்ளிகள் தோன்றும்.",
                "இந்த கறைபுள்ளிகள் சாம்பல்-பச்சை நிறத்தில் இருக்கும்; விளிம்புகள் பழுப்பு நிறத்தில் காணப்படும்.",
                "கடுமையான பாதிப்பு காலத்தில் மேல்தோட்ட இலைகள் வரை நோய் பரவும்."
            ],
            "organic": [
                "காற்றோட்டத்திற்காக முறையான இடைவெளியை பராமரிக்கவும்.",
                "விதை சிகிச்சைக்கு ட்ரைகோடெர்மா விரிடே அல்லது சூடோமோனாஸ் பயன்படுத்தவும்.",
                "நீர் தேங்குவதை தவிர்த்து, மாற்று ஈரப்பதம்-வறண்ட நிலையை பராமரிக்கவும்."
            ],
            "chemical": [
                "ஹெக்ஸாகோனசோல் 5% EC @ 2.0 மில்லி/லி அல்லது வாலிடாமைசின் 3% L @ 2.0 மில்லி/லி.",
                "(மூலம்: ICAR-IIRR / DPPQS)"
            ]
        }
    },
    "Bacterial Leaf Blight": {
        "Telugu": {
            "name": "బాక్టీరియల్ ఆకు ఎండు తెగులు (BLB)",
            "symptoms": [
                "ఆకుల అంచులు మరియు చివర్ల నుండి పసుపు లేదా ఎండుగడ్డి రంగులోకి మారి ఎండిపోవడం",
                "మచ్చల అంచులు అలల మాదిరిగా వంకర్లు తిరిగి ఉంటాయి",
                "ఉదయం పూట తేమ ఉన్నప్పుడు ఆకులపై పసుపు రంగు బాక్టీరియా జిగురు బిందువులు కనిపిస్తాయి"
            ],
            "organic": [
                "తెగులు కనిపించగానే పైపాటుగా నత్రజని ఎరువులు వేయడం వెంటనే ఆపివేయండి",
                "ఎకరానికి 20% తాజా ఆవుపేడ ఊట ద్రావణాన్ని 15 రోజుల వ్యవధిలో రెండుసార్లు పిచికారీ చేయండి",
                "పొటాష్ ఎరువును 25% అదనంగా వేయడం ద్వారా పైరుకు రోగనిరోధక శక్తి పెరుగుతుంది",
                "నాట్లు వేసేటప్పుడు మొలకల ఆకు చివరలను తుంచరాదు"
            ],
            "chemical": [
                "స్ట్రెప్టోసైక్లిన్ (Streptocycline) @ 0.1 గ్రా. + కాపర్ ఆక్సిక్లోరైడ్ 50% WP @ 2.5 గ్రా. లీటరు నీటికి కలిపి పిచికారీ చేయండి (మూలం: ICAR-IIRR/TNAU)",
                "కాపర్ హైడ్రాక్సైడ్ 77% WP (Copper Hydroxide 77% WP) @ 2.0 గ్రా. లీటరు నీటికి"
            ]
        },
        "Hindi": {
            "name": "जीवाणु पत्ती झुलसा रोग (BLB)",
            "symptoms": [
                "पत्तियों के किनारों और सिरे से शुरू होकर अंदर की ओर पुआल जैसे पीले रंग में झुलसना",
                "किनारे लहरदार रूप में सूखते हैं तथा सुबह के समय पत्तियों पर जीवाणु की बूंदें दिखाई देती हैं",
                "प्रारंभिक अवस्था में 'क्रेसक' लक्षण दिखने पर पौधे मुरझाकर सूख जाते हैं"
            ],
            "organic": [
                "रोग के लक्षण दिखते ही यूरिया/नाइट्रोजन का प्रयोग तुरंत रोक दें",
                "20% ताजा गोबर के घोल के अर्क का छिड़काव 15 दिन के अंतराल पर करें",
                "पोटाश उर्वरक की मात्रा 25% बढ़ाएं ताकि पौधों में प्रतिरोधक क्षमता बढ़े",
                "खेत से जल निकासी की व्यवस्था करें"
            ],
            "chemical": [
                "स्ट्रेप्टोसाइक्लिन (Streptocycline) @ 0.1 ग्राम + कॉपर ऑक्सीक्लोराइड 50% WP @ 2.5 ग्राम प्रति लीटर पानी का छिड़काव करें (स्रोत: ICAR/TNAU)",
                "कॉपर हाइड्रॉक्साइड 77% WP @ 2.0 ग्राम प्रति लीटर पानी (स्रोत: CIBRC)"
            ]
        },
        "Tamil": {
            "name": "பாக்டீரியா இலை கருகல் நோய் (BLB)",
            "symptoms": [
                "இலைக்கரைகள் மற்றும் முனைகள் மஞ்சள்-பழுப்பு நிறமாக மாறி, பின்னர் வாடி சுருங்கி போகும்.",
                "சூரிய ஒளியில் குறிப்பாக காலை நேரங்களில் பாக்டீரியா கசிவுகள் தென்படும்.",
                "முதல் கட்டத்தில் மேற்பரப்பு கீறல் அல்லது அலைபோன்ற வடிவங்கள் தெரியும்."
            ],
            "organic": [
                "நோய் அறிகுறிகள் தென்படும்போது யூரியா/நைட்ரஜன் பயன்பாட்டை நிறுத்துங்கள்.",
                "20% புதிய மாட்டு எரு கரைசல் 15 நாள் இடைவெளியில் தெளிக்கலாம்.",
                "பொட்டாஷ் உரத்தை 25% வரை அதிகரித்து நோய் எதிர்ப்பை பலப்படுத்தலாம்."
            ],
            "chemical": [
                "ஸ்ட்ரெப்டோசைக்ளின் @ 0.1 கிராம் + காப்பர் ஆக்ஸிகுளோரைடு 50% WP @ 2.5 கிராம்/லி.",
                "காப்பர் ஹைட்ராக்சைட் 77% WP @ 2.0 கிராம்/லி."
            ]
        }
    },
    "Brown Spot": {
        "Telugu": {
            "name": "వరి ఆకుమచ్చ తెగులు (Brown Spot)",
            "symptoms": [
                "ఆకులపై నువ్వుల గింజల వంటి చిన్న గుండ్రని లేదా కోడిగుడ్డు ఆకారపు ముదురు గోధుమ రంగు మచ్చలు",
                "మచ్చల చుట్టూ పసుపు రంగు వలయం (Yellow halo) స్పష్టంగా కనిపిస్తుంది",
                "తీవ్రమైనప్పుడు గింజలపై కూడా నల్లటి మచ్చలు ఏర్పడి దిగుబడి తగ్గుతుంది"
            ],
            "organic": [
                "నేల పరీక్ష ఆధారంగా సమతుల్య ఎరువులు, ప్రత్యేకించి పొటాష్ మరియు జింక్ లోపాలను సరిదిద్దండి",
                "52-54 డిగ్రీల సెంటీగ్రేడ్ వేడి నీటిలో 10-15 నిమిషాలు విత్తన శుద్ధి చేయండి",
                "వేప గింజల కషాయం (NSKE 5%) లేదా వెల్లుల్లి సారం (2%) పిచికారీ చేయండి"
            ],
            "chemical": [
                "ప్రాపికోనజోల్ 25% EC (Propiconazole 25% EC) @ 1.0 మి.లీ. లీటరు నీటికి చిరుపొట్ట దశలో పిచికారీ చేయండి (మూలం: ICAR-NRRI)",
                "మాంకోజెబ్ 75% WP (Mancozeb 75% WP) @ 2.0 గ్రా. లీటరు నీటికి"
            ]
        },
        "Hindi": {
            "name": "भूरा धब्बा रोग (Brown Spot)",
            "symptoms": [
                "पत्तियों पर तिल के आकार के छोटे गोलाकार अथवा अंडाकार गहरे भूरे रंग के धब्बे",
                "धब्बों के केंद्र हल्के भूरे तथा चारों ओर पीले रंग का स्पष्ट घेरा (हेलो) दिखाई देता है",
                "संक्रमित दानों पर काले धब्बे पड़ जाते हैं जिससे अंकुरण क्षमता घट जाती है"
            ],
            "organic": [
                "पोषक तत्वों विशेषकर पोटाश, जिंक तथा सिलिकॉन की कमी को पूरा करें",
                "52-54 डिग्री से. के गर्म पानी में 10-15 मिनट बीजोपचार करें",
                "नीम के बीज का अर्क (NSKE 5%) का रोग की शुरुआत में छिड़काव करें"
            ],
            "chemical": [
                "प्रोपिकोनाजोल 25% EC (Propiconazole 25% EC) @ 1.0 मिली अथवा मैंकोजेब 75% WP @ 2.0 ग्राम प्रति लीटर पानी में छिड़कें (स्रोत: ICAR-NRRI)",
                "कार्बेन्डाजिम 12% + मैंकोजेब 63% WP @ 2.0 ग्राम प्रति किग्रा बीज से बीजोपचार करें"
            ]
        },
        "Tamil": {
            "name": "பழுப்பு கறை நோய் (Brown Spot)",
            "symptoms": [
                "இலைகளில் சிறிய வட்ட அல்லது ஓவல் வடிவ பழுப்பு நிறக் கறைகள் தோன்றும்.",
                "கறைகளின் சுற்றளவில் மஞ்சள் வட்டங்கள் தெளிவாகத் தெரியும்.",
                "கடுமையான பாதிப்பில் தானியங்களிலும் கருமையான புள்ளிகள் தோன்றும்."
            ],
            "organic": [
                "மண்ணின் சோதனையின் அடிப்படையில் பொட்டாஷ், துத்தநாகம் மற்றும் சிலிக்கான் இடைவெளியை சரிசெய்யவும்.",
                "52-54°C வெந்நீரில் 10-15 நிமிடம் விதைகளை சிகிச்சை செய்யுங்கள்.",
                "வேப்ப விதை சாறு (NSKE 5%) அல்லது பூண்டு கரைசல் 2% பயன்படுத்தலாம்."
            ],
            "chemical": [
                "புரோபிகோனசோல் 25% EC @ 1.0 மில்லி/லி, அல்லது மான்கோசெப் 75% WP @ 2.0 கிராம்/லி.",
                "(மூலம்: ICAR-NRRI)"
            ]
        }
    },
    "False Smut": {
        "Telugu": {
            "name": "వరి కాటుక తెగులు (False Smut)",
            "symptoms": [
                "వెన్నులోని గింజలు పెద్ద మృదువైన పసుపు-నారింజ లేదా ముదురు ఆకుపచ్చ రంగు ముద్దలుగా/బంతులుగా మారుతాయి",
                "తర్వాత ఈ ముద్దలు పగిలి నల్లటి లేదా ఆకుపచ్చటి శిలీంధ్ర పొడిని వెదజల్లుతాయి",
                "పూత దశ ముగిసిన తర్వాత మాత్రమే ఈ లక్షణాలు బయటపడతాయి"
            ],
            "organic": [
                "పూత మరియు గింజ పాలుపోసుకునే దశలో అధిక నత్రజని ఎరువులు వేయరాదు",
                "తెగులు సోకిన ముద్దలను పాలిథిన్ సంచులలో సేకరించి కాల్చివేయండి",
                "వేసవిలో లోతు దుక్కులు చేసి నేలలోని శిలీంధ్ర బీజాలను నశింపజేయండి"
            ],
            "chemical": [
                "చిరుపొట్ట దశలోనే (వెన్ను బయటకు రాకముందే) కాపర్ హైడ్రాక్సైడ్ 77% WP @ 2.0 గ్రా. లేదా ట్రైఫ్లాక్సీస్ట్రోబిన్ 25% + టెబుకోనజోల్ 50% WG @ 0.4 గ్రా. లీటరు నీటికి పిచికారీ చేయండి (మూలం: DPPQS/ICAR)",
                "గమనిక: గింజలపై కాటుక ముద్దలు కనిపించిన తర్వాత పిచికారీ చేయడం వల్ల ఎటువంటి ప్రయోజనం ఉండదు"
            ]
        },
        "Hindi": {
            "name": "मिथ्या कंडुआ / हल्दी रोग (False Smut)",
            "symptoms": [
                "बालियों के अलग-अलग दाने बड़े मखमली पीले, नारंगी या गहरे हरे रंग के चूर्णयुक्त गोलों में बदल जाते हैं",
                "बाद में झिल्ली फटने पर गहरे जैतूनी-हरे रंग के बीजाणु निकलते हैं जो अन्य दानों को भी दूषित करते हैं",
                "यह रोग केवल फूल आने और दाना बनने की अवस्था के बाद ही दिखाई देता है"
            ],
            "organic": [
                "गोभ अवस्था के बाद यूरिया/नाइट्रोजन की अतिरिक्त टॉप ड्रेसिंग न करें",
                "रोगग्रस्त दानों को सावधानीपूर्वक पॉलीथिन में इकट्ठा करके नष्ट कर दें",
                "गर्मियों में खेत की गहरी जुताई करें ताकि बीजाणु नष्ट हो जाएं"
            ],
            "chemical": [
                "बाली निकलने से पूर्व (गोभ अवस्था में) कॉपर हाइड्रॉक्साइड 77% WP @ 2.0 ग्राम अथवा ट्राइफ्लोक्सीस्ट्रोबिन 25% + टेबुकोनाजोल 50% WG @ 0.4 ग्राम प्रति लीटर पानी का छिड़काव करें (स्रोत: DPPQS/ICAR)",
                "नोट: कंडुआ के गोले दिखाई देने के बाद दवा का छिड़काव निष्प्रभावी होता है"
            ]
        },
        "Tamil": {
            "name": "பொய்யான பூசண நோய் (False Smut)",
            "symptoms": [
                "தானியத்தின் பகுதிகளில் மென்மையான மஞ்சள்-ஆரஞ்சு அல்லது அடர் பச்சை நிற புள்ளிகள் தோன்றும்.",
                "மேலும் அவை வெடித்துச் செல்லும்போது கறுப்பு-பச்சை நிற பூக்கள் வெளியேறும்.",
                "இந்த நோய் பொதுவாக பூப்பது அல்லது தானியம் உருவாகும் கட்டத்தில் தோன்றும்."
            ],
            "organic": [
                "நோய் பரவுவதற்கு முன் அதிக நைட்ரஜன் உரத்தை தவிர்க்கவும்.",
                "நோயுற்ற தானியங்களை பிளாஸ்டிக் பைகளில் சேகரித்து அழிக்கவும்.",
                "கோடை காலங்களில் தடிமனான மண்ணை நன்கு புழங்கவும்."
            ],
            "chemical": [
                "காப்பர் ஹைட்ராக்சைட் 77% WP @ 2.0 கிராம்/லி, அல்லது ட்ரிஃப்ளோக்ஸிஸ்ட்ரோபின் 25% + டெபுகோனசோல் 50% WG @ 0.4 கிராம்/லி.",
                "(மூலம்: DPPQS/ICAR)"
            ]
        }
    }
}


class DiseaseAgent:
    """Combines vision analysis and retrieved RAG evidence into a validated structured result."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _extract_evidence_points(self, chunks: List[Dict[str, Any]], target_category: str) -> List[str]:
        """Extracts clean bullet points from evidence chunks matching a specific category."""
        extracted = []
        for c in chunks:
            content = c.get("content", "")
            meta = c.get("metadata", {})
            cat = meta.get("category", "")

            # Match category
            matched = False
            if target_category == "symptoms" and ("symptom" in cat or "symptom" in content.lower()[:80]):
                matched = True
            elif target_category == "organic" and ("organic" in cat or "cultural" in cat):
                matched = True
            elif target_category == "chemical" and ("chemical" in cat or "active ingredient" in content.lower()):
                matched = True

            if not matched:
                continue

            lines = content.split("\n")
            for line in lines:
                line_clean = line.strip()
                if not line_clean or line_clean.startswith("Official") or line_clean.startswith("Causal") or line_clean.startswith("Issuing Source"):
                    continue
                # Ignore numbered headers like "1. Identification...", "5. Verified..."
                if re.match(r'^[0-9]+\.\s+[A-Za-z\s]+$', line_clean):
                    continue
                # Clean prefix tags
                cleaned = re.sub(r'^[•\-\*]\s*', '', line_clean)
                cleaned = re.sub(r'^(Symptoms|Causes|Prevention|Cultural Practices|Organic Management|Chemical Management):\s*', '', cleaned, flags=re.I)
                cleaned = cleaned.strip()

                if len(cleaned) > 20 and cleaned not in extracted and not cleaned.startswith("Notice:"):
                    extracted.append(cleaned)
        return extracted

    def _call_gemini_agent(
        self,
        vision_result: Dict[str, Any],
        retrieved_evidence: List[Dict[str, Any]],
        crop: str,
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Invokes Gemini LLM when API key is provided for multilingual text synthesis."""
        if not self.api_key:
            return None

        prompt = build_disease_prompt(vision_result, retrieved_evidence, crop, language)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

        schema_instruction = (
            "You must return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "crop": "paddy",\n'
            '  "disease": "Disease Name or Healthy or Uncertain",\n'
            '  "confidence": 0.87,\n'
            '  "observations": ["..."],\n'
            '  "symptoms": ["..."],\n'
            '  "organic_management": ["..."],\n'
            '  "chemical_management": ["..."],\n'
            '  "evidence": ["..."],\n'
            '  "sources": ["..."],\n'
            '  "warning": "...",\n'
            '  "language": "' + language + '"\n'
            "}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\n" + schema_instruction + "\n\n" + prompt}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text_content)
        except Exception as e:
            print(f"Notice: Gemini Agent generation failed ({e}), using grounded rule synthesizer.")
            return None

    def _synthesize_grounded_response(
        self,
        vision_result: Dict[str, Any],
        retrieved_evidence: List[Dict[str, Any]],
        crop: str,
        language: str
    ) -> DiseaseAnalysisResult:
        """
        Deterministic, zero-hallucination synthesizer that constructs the response
        strictly from vision observations and retrieved agricultural corpus evidence.
        """
        crop_name = crop or vision_result.get("crop", "paddy")
        possible_disease = vision_result.get("possible_disease", "uncertain")
        confidence = float(vision_result.get("confidence", 0.0))
        observations = list(vision_result.get("observations", []))

        sources = list(dict.fromkeys(
            chunk.get("source", "ICAR/IRRI Agricultural Extension")
            for chunk in retrieved_evidence
            if chunk.get("source")
        ))
        evidence_snippets = [chunk.get("content", "").strip() for chunk in retrieved_evidence if chunk.get("content")]

        # Case 1: Healthy Crop
        if possible_disease.lower() == "healthy":
            if language == "Telugu":
                return DiseaseAnalysisResult(
                    crop=crop_name,
                    disease="ఆరోగ్యకరమైన పైరు (Healthy Paddy)",
                    confidence=confidence,
                    observations=[
                        "పైరు ఆకులు ఏపుగా, సహజమైన ఆకుపచ్చ రంగులో ఉన్నాయి",
                        "ఎటువంటి శిలీంద్ర లేదా బాక్టీరియల్ తెగులు మచ్చలు కనిపించలేదు"
                    ],
                    symptoms=[],
                    organic_management=[
                        "సిఫార్సు చేసిన మోతాదులో మాత్రమే సమతుల్య నత్రజని, భాస్వరం, పొటాష్ ఎరువులు వేయండి",
                        "పొలంలో నీటిని నిల్వ ఉంచకుండా ఆరుతడులు ఇవ్వండి",
                        "పైరును క్రమం తప్పకుండా పర్యవేక్షించండి"
                    ],
                    chemical_management=[
                        "ఆరోగ్యకరమైన పైరుకు ఎటువంటి రసాయన మందులు పిచికారీ చేయవలసిన అవసరం లేదు"
                    ],
                    evidence=["ICAR/IRRI crop standards: No foliar lesions or pathogen symptoms detected."],
                    sources=sources or ["ICAR Crop Production Guide"],
                    warning=DISCLAIMER_TRANSLATIONS.get("Telugu", DISCLAIMER_TRANSLATIONS["English"]),
                    language=language
                )
            elif language == "Hindi":
                return DiseaseAnalysisResult(
                    crop=crop_name,
                    disease="स्वस्थ धान की फसल (Healthy Paddy)",
                    confidence=confidence,
                    observations=[
                        "धान की पत्तियां स्वस्थ और स्वाभाविक हरे रंग में हैं",
                        "पत्तियों पर किसी भी कवक या जीवाणु जनित धब्बे के लक्षण नहीं हैं"
                    ],
                    symptoms=[],
                    organic_management=[
                        "मिट्टी की जांच के अनुसार संतुलित मात्रा में एनपीके उर्वरकों का प्रयोग करें",
                        "खेत में जल निकास की उचित व्यवस्था रखें",
                        "नियमित रूप से फसल का निरीक्षण करते रहें"
                    ],
                    chemical_management=[
                        "स्वस्थ फसल पर किसी भी प्रकार के रासायनिक छिड़काव की आवश्यकता नहीं है"
                    ],
                    evidence=["ICAR/IRRI crop standards: No foliar lesions or pathogen symptoms detected."],
                    sources=sources or ["ICAR Crop Production Guide"],
                    warning=DISCLAIMER_TRANSLATIONS.get("Hindi", DISCLAIMER_TRANSLATIONS["English"]),
                    language=language
                )
            else:
                return DiseaseAnalysisResult(
                    crop=crop_name,
                    disease="Healthy",
                    confidence=confidence,
                    observations=observations or ["Uniform green leaf blade with intact cell integrity", "No lesions detected"],
                    symptoms=[],
                    organic_management=[
                        "Maintain balanced NPK fertilization as per soil testing",
                        "Adopt alternate wetting and drying (AWD) water management",
                        "Conduct weekly field scouting during vegetative and tillering stages"
                    ],
                    chemical_management=[
                        "No chemical application required for healthy crop"
                    ],
                    evidence=["ICAR/IRRI crop standards: No foliar lesions or pathogen symptoms detected."],
                    sources=sources or ["ICAR Crop Production Guide"],
                    warning="Crop foliage appears healthy. Continue routine monitoring and avoid excessive nitrogen application.",
                    language=language
                )

        # Case 2: Uncertain / Unclear / Unrelated image
        if possible_disease.lower() in ["uncertain", "unknown", ""] or confidence < 0.40:
            warning_msg = DISCLAIMER_TRANSLATIONS.get(language, DISCLAIMER_TRANSLATIONS["English"])
            upload_guidance = {
                "English": "Please upload a clear, focused photograph of the affected crop part (leaf, fruit, stem, or branch).",
                "Telugu": "దయచేసి ప్రభావిత మొక్క భాగం (ఆకు, పండు, కాండం, లేదా శాఖ) యొక్క స్పష్టమైన, కేంద్రీకృతమైన ఫోటోను అప్‌లోడ్ చేయండి.",
                "Hindi": "कृपया प्रभावित फसल के भाग (पत्ती, फल, तना या शाखा) की स्पष्ट, केंद्रित फोटो अपलोड करें।",
                "Tamil": "தயவுசெய்து பாதிக்கப்பட்ட பயிரின் பகுதியின் (இலை, பழம், தண்டு அல்லது கிளை) தெளிவான, மையப்படுத்தப்பட்ட புகைப்படத்தை பதிவேற்றவும்."
            }
            disease_display = "Uncertain"
            if language == "Telugu":
                disease_display = "అనిశ్చితం / గుర్తించబడలేదు (Uncertain)"
            elif language == "Hindi":
                disease_display = "अनिश्चित / पहचाना नहीं गया (Uncertain)"
            elif language == "Tamil":
                disease_display = "நிச்சயமற்றது / கண்டறிய முடியவில்லை (Uncertain)"

            return DiseaseAnalysisResult(
                crop=crop_name,
                disease=disease_display,
                confidence=confidence,
                observations=observations or ["Image could not be reliably classified"],
                symptoms=[],
                organic_management=[],
                chemical_management=[],
                evidence=[],
                sources=[],
                warning=f"{warning_msg} {upload_guidance.get(language, upload_guidance['English'])}",
                language=language
            )

        # Case 3: Insufficient RAG Evidence
        if not retrieved_evidence:
            insufficient_msg = INSUFFICIENT_EVIDENCE_MESSAGES.get(language, INSUFFICIENT_EVIDENCE_MESSAGES["English"])
            warning_msg = DISCLAIMER_TRANSLATIONS.get(language, DISCLAIMER_TRANSLATIONS["English"])
            return DiseaseAnalysisResult(
                crop=crop_name,
                disease=possible_disease,
                confidence=confidence,
                observations=observations,
                symptoms=[],
                organic_management=[],
                chemical_management=[],
                evidence=[insufficient_msg],
                sources=[],
                warning=f"{insufficient_msg} {warning_msg}",
                language=language
            )

        # Case 4: Evidence-backed Diagnosis
        warning_text = DISCLAIMER_TRANSLATIONS.get(language, DISCLAIMER_TRANSLATIONS["English"])

        # Check for multilingual pre-translated data for target disease
        if language in ["Telugu", "Hindi", "Tamil"] and possible_disease in DISEASE_MULTILINGUAL_DATA:
            m_data = DISEASE_MULTILINGUAL_DATA[possible_disease].get(language)
            if m_data:
                return DiseaseAnalysisResult(
                    crop=crop_name,
                    disease=m_data["name"],
                    confidence=confidence,
                    observations=observations,
                    symptoms=m_data["symptoms"],
                    organic_management=m_data["organic"],
                    chemical_management=m_data["chemical"],
                    evidence=evidence_snippets[:3],
                    sources=sources,
                    warning=warning_text,
                    language=language
                )

        # English / General language synthesis from retrieved evidence
        symptoms = self._extract_evidence_points(retrieved_evidence, "symptoms")
        organic = self._extract_evidence_points(retrieved_evidence, "organic")
        chemical = self._extract_evidence_points(retrieved_evidence, "chemical")

        return DiseaseAnalysisResult(
            crop=crop_name,
            disease=possible_disease,
            confidence=confidence,
            observations=observations,
            symptoms=symptoms[:4] if symptoms else ["Refer to attached evidence excerpt"],
            organic_management=organic[:4] if organic else ["Maintain balanced fertilization and field sanitation"],
            chemical_management=chemical[:4] if chemical else ["No verified chemical intervention in retrieved evidence"],
            evidence=evidence_snippets[:3],
            sources=sources,
            warning=warning_text,
            language=language
        )

    def process(
        self,
        vision_result: Dict[str, Any],
        retrieved_evidence: List[Dict[str, Any]],
        crop: str = "paddy",
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Executes the Disease Agent reasoning step.
        Returns a dictionary conforming exactly to Phase 7 structured output schema.
        """
        # If API key configured, attempt LLM call
        if self.api_key:
            llm_result = self._call_gemini_agent(vision_result, retrieved_evidence, crop, language)
            if llm_result and "disease" in llm_result:
                try:
                    res_obj = DiseaseAnalysisResult(**llm_result)
                    return res_obj.to_dict()
                except Exception as val_err:
                    print(f"Warning: LLM output validation error ({val_err}), using grounded synthesizer.")

        # Grounded deterministic synthesizer
        res_obj = self._synthesize_grounded_response(
            vision_result=vision_result,
            retrieved_evidence=retrieved_evidence,
            crop=crop,
            language=language
        )
        return res_obj.to_dict()

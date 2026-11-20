# Failure analysis (full)

237 (query, variant) pairs where the full pipeline gets nDCG@10 = 0 but native BM25 succeeds; 15 sampled.

## 596559#0 (roman)
- native: घर्षण द्वारा किए गए कार्य का क्षय नहीं होता है बल्कि यह ऊर्जा में रूपांतरित हो जाती है?
- query: `gharsan dwara kiye gaye karya ka kshay nahi hota hai balki yeh urja mein roopantarit ho jati hai?`
- normalised: `घरसन घरसान gharsan द्वार dwara किय किए kiye गय गाय gaye कार्य कर्य karya क्षय क्षय् kshay नह नाह nahi बालक बल्क balki येह yeh उर्ज ऊर्ज urja रूपान्तर रूपांतर roopantarit एचओ ho जा जात jati`
- tokens: gharsan→घरसन, dwara→द्वारा, kiye→किये, gaye→गये, karya→कार्य, ka→-, kshay→क्षय, nahi→नही, hota→-, hai→-, balki→बालकी, yeh→येह, urja→उर्जा, mein→-, roopantarit→रूपान्तरित, ho→हो, jati→जाती, hai→-
- top-3 retrieved: सरल यंत्र | नवीकरणीय संसाधन | अक्षय ऊर्जा
- relevant: ऊष्मा का इतिहास | ऊष्मीय दक्षता | ऊर्जा

## 707104#0 (roman)
- native: ऐतिहासिक स्मारक का निर्माण नारनौल के जागीरदार शाह कुली खान द्वारा कब करवाया गया था?
- query: `aitihasik smarak ka nirmaan Narnaual ke jagirdar Shah Kuli Khan dwara kab karvaya gaya tha?`
- normalised: `ऐतिहास ऐतिहस aitihasik स्मारक स्मरक smarak निर्माण निरमाण nirmaan नरनौअल नरनौआल narnaual जागीरदार जागिरदार jagirdar शाह शह shah कुल कुल kuli खान खन khan द्वार dwara करव कारव karvaya गाय gaya`
- tokens: aitihasik→ऐतिहासिक, smarak→स्मारक, ka→-, nirmaan→निर्माण, narnaual→नरनौअल, ke→-, jagirdar→जागीरदार, shah→शाह, kuli→कुली, khan→खान, dwara→द्वारा, kab→-, karvaya→करवाया, gaya→गया, tha→-
- top-3 retrieved: नारनौल | ढाका | नवाब शेख अब्दुल्ला
- relevant: महेंद्रगढ़

## 1262944#0 (mix75)
- native: भारत का सबसे ऊँचा बाँध टिहरी बाँध है और किस नदी पर बना है?
- query: `India ka highest dam Tihri Dam hai and on which river is it built?`
- normalised: `इंड इंद भारत india हाइस्ट हाइजेस्ट ऊँच highest दम डैम बंदर डैम dam तिहर टिहर tihri दम डैम बंदर डैम dam रिवर राइवर नद river बिल्ट बुइल्ट निर्म built`
- tokens: india→इंडिया (+भारत), ka→-, highest→हाइस्ट (+सबसे ऊँचा), dam→दम (+बंदर/डैम), tihri→तिहरी, dam→दम (+बंदर/डैम), hai→-, river→रिवर (+नदी), built→बिल्ट (+निर्मित)
- top-3 retrieved: गेतलसूद डैम | चिपलून | गरगा नदी
- relevant: गंगा के बाँध एवं नदी परियोजनाएँ | भागीरथी नदी | टिहरी बाँध

## 231597#0 (mix75)
- native: विश्व प्रसिद्ध खारे जल की झील सांभर किस राज्य में स्थित है?
- query: `world famous salty water lake sambhar is located in which state?`
- normalised: `वर्ल्ड वोर्ल्ड विश्व world फेमस फैमस प्रसिद्ध famous साल्ट सैल्ट नमकीन salty वाटर वॉटर पा water लेक लाक झील lake संभार संभर sambhar लोकेटेड लोकेटिड स्थ located स्टेट स्टेट राज्य स्टेट state`
- tokens: world→वर्ल्ड (+विश्व), famous→फेमस (+प्रसिद्ध), salty→साल्टी (+नमकीन), water→वाटर (+पानी), lake→लेक (+झील), sambhar→संभार, located→लोकेटेड (+स्थित), state→स्टेट (+राज्य/स्टेट)
- top-3 retrieved: ग्वालदम स्टेट | खारी झील | भारतीय स्टेट बैंक
- relevant: साम्भर झील | राजस्थान की झीलें

## 1207940#0 (mix50)
- native: जानवरों के अध्ययन को क्या कहते हैं?
- query: `animals study what is called?`
- normalised: `एनिमल्स एनीमल्स पश जीव animals स्टड स्टुड अध्ययन अभ्यास study कॉल्ड काल्ड कॉल called`
- tokens: animals→एनिमल्स (+पशु/जीव), study→स्टडी (+अध्ययन/अभ्यास), called→कॉल्ड (+कहा गया/कॉल किया)
- top-3 retrieved: नफीसा जोसेफ | जीव विज्ञान | जीव विज्ञान
- relevant: जन्तुओं का विस्तार | जन्तुभूगोल | मानस शास्त्र

## 229888#0 (mix75)
- native: भारत ने पहला परमाणु परीक्षण कब और कहाँ किया था?
- query: `india ne first nuclear test when and where kiya tha?`
- normalised: `इंड इंद भारत india फर्स्ट फ़र्स्ट पहल first न्यूक्लियर न्यूक्लीयर परमाण nuclear टेस्ट टैस्ट परीक्षण टेस्ट test कीय kiya`
- tokens: india→इंडिया (+भारत), ne→-, first→फर्स्ट (+पहला), nuclear→न्यूक्लियर (+परमाणु), test→टेस्ट (+परीक्षण/टेस्ट), kiya→किया, tha→-
- top-3 retrieved: न्यूक्लियर पावर कॉर्पोरेशन ऑफ इंडिया लिमिटेड | पैड एबॉर्ट परीक्षण 1 | भरत कर्नाड
- relevant: भारतीय परमाणु परीक्षण | परमाणु परीक्षण | भारत में सामूहिक विनाश के हथियार

## 853675#0 (mix75)
- native: सभी पौधों के लिए कितने पोषक तत्व अति आवश्यक होते हैं?
- query: `how many essential nutrients do all plants need?`
- normalised: `मै मा many एसेंशियल इसेंशियल आवश्यक essential न्यूट्रिएंट्स न्यूट्रीएंट्स पोषक तत्व nutrients अल्ल अल all प्लांट्स प्लान्ट्स पौध plants नीड नीद ज़रूरत निड need`
- tokens: many→मैनी (+बहुत/कई), essential→एसेंशियल (+आवश्यक), nutrients→न्यूट्रिएंट्स (+पोषक तत्व), all→अल्ल (+सभी), plants→प्लांट्स (+पौधे), need→नीड (+ज़रूरत/निड)
- top-3 retrieved: सूक्ष्म पोषक तत्व | विंडोज़ एसेंशियल बिज़नेस सर्वर २००८ | पोषक तत्व
- relevant: पादप पोषण

## 230374#0 (mix75)
- native: शान्तिनिकेतन की स्थापना किसने की?
- query: `shantiniketan ki foundation kisne ki?`
- normalised: `शांतिनिकेतन शान्तिनिकेतन shantiniketan फाउंडेशन फाउण्डेशन आधार foundation`
- tokens: shantiniketan→शांतिनिकेतन, ki→-, foundation→फाउंडेशन (+आधार), kisne→-, ki→-
- top-3 retrieved: आर्ट ऑफ लिविंग फाउण्डेशन | आगरी कोली यूथ फाउंडेशन | अन्तर्राष्ट्रीय दिव्यांग दिवस
- relevant: शान्तिनिकेतन | शान्तिनिकेतन | विश्व-भारती विश्वविद्यालय

## 596559#0 (mix50)
- native: घर्षण द्वारा किए गए कार्य का क्षय नहीं होता है बल्कि यह ऊर्जा में रूपांतरित हो जाती है?
- query: `friction dwara kiye gaye work ka loss nahi hota balki yeh energy mein convert ho jati hai?`
- normalised: `फ्रिक्शन फ्रिकशन घर्षण friction द्वार dwara किय किए kiye गय गाय gaye वर्क वोर्क काम work लॉस लोस हान loss नह नाह nahi बालक बल्क balki येह yeh एनर्ज इनर्ज ऊर्ज energy कन्वर्ट कनवर्ट परिवर्त रूपांतर convert एचओ ho जा जात jati`
- tokens: friction→फ्रिक्शन (+घर्षण), dwara→द्वारा, kiye→किये, gaye→गये, work→वर्क (+काम), ka→-, loss→लॉस (+हानि), nahi→नही, hota→-, balki→बालकी, yeh→येह, energy→एनर्जी (+ऊर्जा), mein→-, convert→कन्वर्ट (+परिवर्तित/रूपांतरित), ho→हो, jati→जाती, hai→-
- top-3 retrieved: भाप टरबाइन | ऊर्जा का रूपान्तरण | बेयरिंग
- relevant: ऊष्मा का इतिहास | ऊष्मीय दक्षता | ऊर्जा

## 49940#0 (mix75)
- native: अगर किसी मिश्रधातु में एक धातु पारद है तो इसे क्या कहते हैं?
- query: `agar kisi alloy mein ek metal present hai to it is called kya?`
- normalised: `अगर अगार agar कीस kisi अलॉय एलॉय मिश्र धात मिश्र धात alloy मेटल मेटाल धात metal प्रेजेंट प्रजेंट उपस्थ उपहार present कॉल्ड काल्ड कॉल called`
- tokens: agar→अगर, kisi→किसी, alloy→अलॉय (+मिश्र धातु/मिश्र धातु), mein→-, ek→-, metal→मेटल (+धातु), present→प्रेजेंट (+उपस्थित/उपहार), hai→-, called→कॉल्ड (+कहा गया/कॉल किया), kya→-
- top-3 retrieved: मिश्रातु | एलॉय व्हील (मिश्र धातु के पहिये) | धातु चद्दर
- relevant: पारा | संलय

## 584627#0 (mix50)
- native: किस राज्य के मुख्यमंत्री वाईएस जगन मोहन रेड्डी ने एप्प लांच किया है?
- query: `kis state ke CM ys jagn mohan reddi ne app launch kiya hai?`
- normalised: `स्टेट स्टेट राज्य स्टेट state सीएम सिएम सेंटीमीटर cm यस् यस ys जग्न जगन jagn मोहन मोहान mohan रेड्ड रेद्द reddi अप्प एप ऐप app लॉन्च लौंच लॉन्च launch कीय kiya`
- tokens: kis→-, state→स्टेट (+राज्य/स्टेट), ke→-, cm→सीएम (+सेंटीमीटर), ys→यस्, jagn→जग्न, mohan→मोहन, reddi→रेड्डी, ne→-, app→अप्प (+ऐप), launch→लॉन्च (+लॉन्च), kiya→किया, hai→-
- top-3 retrieved: एडएक्स | न्यूज़ स्टेट | न्यूज़ स्टेट
- relevant: वाई एस जगनमोहन रेड्डी | नरेन्द्र मोदी | नरेंद्र मोदी का दूसरा शपथ ग्रहण समारोह

## 839841#0 (mix50)
- native: अर्जुन ने आँख पर पटी बांध क्र किस जानवर की आंख में निशाना लगाया था?
- query: `arjun ne eye par pati baandh kar kis animal ki eye mein target lagaya tha?`
- normalised: `अर्जुन अर्जून arjun एय इय आँख eye पाट पत pati बाँध बांध baandh कर कार kar एनिमल एनीमल पश जीव animal एय इय आँख eye टारगेट टार्गट लक्ष्य target लग लाग lagaya`
- tokens: arjun→अर्जुन, ne→-, eye→एये (+आँख), par→-, pati→पाटी, baandh→बाँध, kar→कर, kis→-, animal→एनिमल (+पशु/जीव), ki→-, eye→एये (+आँख), mein→-, target→टारगेट (+लक्ष्य), lagaya→लगाया, tha→-
- top-3 retrieved: मानव शरीर | काली आँख गैलेक्सी | रोगों की सूची
- relevant: कर्ण | महाभारत भाग १०

## 230382#0 (mix75)
- native: भारत में नालंदा विश्वविद्यालय किस राज्य में स्थित था?
- query: `india mein nalanda university kis state mein located was?`
- normalised: `इंड इंद भारत india नालंद नलंद nalanda यूनिवर्सिट युनिवर्सिट विश्वविद्यालय university स्टेट स्टेट राज्य स्टेट state लोकेटेड लोकेटिड स्थ located`
- tokens: india→इंडिया (+भारत), mein→-, nalanda→नालंदा, university→यूनिवर्सिटी (+विश्वविद्यालय), kis→-, state→स्टेट (+राज्य/स्टेट), mein→-, located→लोकेटेड (+स्थित)
- top-3 retrieved: भारतीय स्टेट बैंक | दक्षिण उरल स्टेट यूनिवर्सिटी | संक्षिप्त सन्देश सेवा
- relevant: भारत के सात आश्चर्य | भारत के प्राचीन विश्वविद्यालय | नालन्दा महाविहार

## 188524#0 (mix75)
- native: कौन सा पुल भारत की मुख्य भूमि को रामेश्वरम द्वीप से अलग करता है?
- query: `which bridge india main land separates rameshwaram island?`
- normalised: `ब्रिज ब्रीज पुल ब्रिज bridge इंड इंद भारत india लैंड लैण्ड जमीन land सेपरेट्स सेपेरेट्स अलग separates रामेश्वरम रामेश्वरम् rameshwaram आईएसएलएंड आईएसलैंड द्वीप island`
- tokens: bridge→ब्रिज (+पुल/ब्रिज), india→इंडिया (+भारत), main→-, land→लैंड (+जमीन), separates→सेपरेट्स (+अलग करता है), rameshwaram→रामेश्वरम, island→आईएसएलएंड (+द्वीप)
- top-3 retrieved: ढलवां लोहा | रामेश्वरम द्वीप | वुडफ़र्ड ब्रिज
- relevant: रामेश्वरम तीर्थ | रामेश्वरम शहर | रामेश्वरम शहर

## 95604#0 (mix75)
- native: गोताखोर पानी के अंदर सांस लेने के लिए कौन कौन सी गैसों का मिश्रण ले जाते हैं?
- query: `diver underwater breathing ke liye kaun kaun si gases ka mix le jate hain?`
- normalised: `डाइवर डायवर डाइवर diver अंडरवाटर अंडरवॉटर जलमग्न underwater ब्रीथिंग ब्रेथिंग सांस ले श्वसन breathing liye एसआई सी si गेसेस गेस गैस gases मिक्स मीक्स मिश्रण mix ले ली le जा जत jate`
- tokens: diver→डाइवर (+डाइवर), underwater→अंडरवाटर (+जलमग्न), breathing→ब्रीथिंग (+सांस लेना/श्वसन), ke→-, liye→लिये, kaun→-, kaun→-, si→एसआई, gases→गेसेस (+गैस), ka→-, mix→मिक्स (+मिश्रण), le→ले, jate→जाते, hain→-
- top-3 retrieved: उदरीय श्वसन | श्याओमी मि मिक्स ३ | श्वसन तंत्र
- relevant: स्कूबा डाइविंग

# Failure analysis (sample)

229 (query, variant) pairs where the full pipeline gets nDCG@10 = 0 but native BM25 succeeds; 15 sampled.

## 723420#0 (roman)
- native: लसीका किससे पचा हुआ तथा अवशोषित वसा का वहां करती है?
- query: `lasika kis se pachha hua tatha avshoshit vasa ka wahan karti hai?`
- normalised: `लसिक लसीक lasika पछ पाछ pachha तथ टाठ tatha अवशोष आवशोष avshoshit वस वस vasa वहान वहन wahan कर कर् karti`
- tokens: lasika→लसिका, kis→-, se→-, pachha→पछा, hua→-, tatha→तथा, avshoshit→अवशोषित, vasa→वसा, ka→-, wahan→वहान, karti→करती, hai→-
- top-3 retrieved: विकृतिविज्ञान | आहार और आहारविद्या | नारियल तेल
- relevant: लसीका तंत्र

## 735588#0 (roman)
- native: सम्पूर्ण भारत में गेहूँ की ट्रिटिकम एस्टीवम प्रजाति उगाई जाती है तथा अन्य मुख्य प्रजाति है?
- query: `sampoorna bharat mein gehun ki tritikam estivam prajati ugaai jaati hai tatha anya mukhya prajati hai?`
- normalised: `संपूर्ण सम्पूर्ण sampoorna भारत भरत bharat गेहुन गेहूँ gehun तृतिकाम तृतिकम tritikam एस्टिवम एस्टीवम estivam प्रजात प्रज prajati उग ऊग ugaai जा जात jaati तथ टाठ tatha अन्य अनय anya मुख्य मुखय mukhya प्रजात प्रज prajati`
- tokens: sampoorna→संपूर्ण, bharat→भारत, mein→-, gehun→गेहुन, ki→-, tritikam→तृतिकाम, estivam→एस्टिवम, prajati→प्रजाति, ugaai→उगाई, jaati→जाती, hai→-, tatha→तथा, anya→अन्य, mukhya→मुख्य, prajati→प्रजाति, hai→-
- top-3 retrieved: नीलगिरी (यूकलिप्टस) | ब्लैक-रम्प्ड फ्लेमबैक | आम
- relevant: गेहूँ | गेहूँ

## 1167291#0 (mix75)
- native: भारत में पंचायती राज की अनुशंसा की थी?
- query: `bharat mein panchayat government recommendation ki thi?`
- normalised: `भारत भरत bharat पंचायत पञ्चायत panchayat गवर्नमेंट गवर्नमेन्ट सरकार government रिकमेंडेशन रीकमेंडेशन सिफारिश recommendation`
- tokens: bharat→भारत, mein→-, panchayat→पंचायत, government→गवर्नमेंट (+सरकार), recommendation→रिकमेंडेशन (+सिफारिश), ki→-, thi→-
- top-3 retrieved: केन्द्रीय सरकार स्वास्थ्य योजना | भारत के प्रमुख अस्पताल | उत्तर प्रदेश में पंचायती राज्य
- relevant: पंचायती राज

## 230231#0 (mix75)
- native: चमगादड़ किस कारण से अंधेरे में उड़ सकता है?
- query: `bat kis reason se dark mein fly kar sakta hai?`
- normalised: `बट बाट बल्ल bat रीजन रीज़न कारण reason डार्क दर्क अंधेर गहर dark फ्ल फ्ल उड़ fly कर कार kar सक् sakta`
- tokens: bat→बट (+बल्ला), kis→-, reason→रीजन (+कारण), se→-, dark→डार्क (+अंधेरा/गहरा), mein→-, fly→फ्लाई (+उड़ना), kar→कर, sakta→सकता, hai→-
- top-3 retrieved: क्या आप अंधेरे से डरते हैं? एपिसोड की सूची | चमगादड़ | कीट
- relevant: चमगादड़ गण

## 1174018#0 (mix50)
- native: 1947 में भारत के स्वतंत्र होने के पश्चात तक हरियाणा किस प्रान्त का भाग था?
- query: `1947 mein India ke independent hone ke pashchat tak Haryana kis state ka bhag tha?`
- normalised: `1947 इंड इंद भारत india इंडिपेंडेंट इंडीपेंडेंट स्वतंत्र independent होन hone पश्चात पशचात pashchat हरयाण हरियाण haryana स्टेट स्टेट राज्य स्टेट state भाग भग bhag`
- tokens: mein→-, india→इंडिया (+भारत), ke→-, independent→इंडिपेंडेंट (+स्वतंत्र), hone→होने, ke→-, pashchat→पश्चात, tak→-, haryana→हरयाणा, kis→-, state→स्टेट (+राज्य/स्टेट), ka→-, bhag→भाग, tha→-
- top-3 retrieved: स्टेट बैंक ऑफ़ मैसूर | भवनजी अर्जुन खिमजी | इस्लामिक स्टेट ऑफ़ इराक एंड लेवेंट - सिनाई प्रांत
- relevant: हरियाणा | हरियाणा का इतिहास

## 20617#0 (mix75)
- native: क्षेत्रफल में भारत का सबसे बड़ा राज्य कौन है?
- query: `area mein india ka biggest state which is?`
- normalised: `एआरईए आर क्षेत्र क्षेत्रफल area इंड इंद भारत india बिगेस्ट बिगस्ट बड़ बड़ biggest स्टेट स्टेट राज्य स्टेट state`
- tokens: area→एआरईए (+क्षेत्र/क्षेत्रफल), mein→-, india→इंडिया (+भारत), ka→-, biggest→बिगेस्ट (+सबसे बड़ा/बड़ा), state→स्टेट (+राज्य/स्टेट)
- top-3 retrieved: स्टेट बैंक ऑफ़ मैसूर | इस्लामिक स्टेट ऑफ़ इराक एंड लेवेंट - सिनाई प्रांत | भारत में बैंकिंग
- relevant: राजस्थान का भूगोल | राजस्थान के शहर | राजस्थान

## 584627#0 (roman)
- native: किस राज्य के मुख्यमंत्री वाईएस जगन मोहन रेड्डी ने एप्प लांच किया है?
- query: `kis rajya ke mukhya mantri ys jagn mohan reddi ne app launch kiya hai?`
- normalised: `राज्य राजय rajya मुख्य मुखय mukhya मंत्र मन्त्र mantri यस् यस ys जग्न जगन jagn मोहन मोहान mohan रेड्ड रेद्द reddi अप्प एप ऐप app लॉन्च लौंच लॉन्च launch कीय kiya`
- tokens: kis→-, rajya→राज्य, ke→-, mukhya→मुख्य, mantri→मंत्री, ys→यस्, jagn→जग्न, mohan→मोहन, reddi→रेड्डी, ne→-, app→अप्प (+ऐप), launch→लॉन्च (+लॉन्च), kiya→किया, hai→-
- top-3 retrieved: आत्मनिर्भर भारत | भारतीय अंतरिक्ष अनुसंधान संगठन | आरोग्य सेतु
- relevant: वाई एस जगनमोहन रेड्डी | नरेन्द्र मोदी | नरेंद्र मोदी का दूसरा शपथ ग्रहण समारोह

## 95604#0 (mix75)
- native: गोताखोर पानी के अंदर सांस लेने के लिए कौन कौन सी गैसों का मिश्रण ले जाते हैं?
- query: `diver underwater breathing ke liye kaun kaun si gases ka mix le jate hain?`
- normalised: `डाइवर डायवर डाइवर diver अंडरवाटर अंडरवॉटर जलमग्न underwater ब्रीथिंग ब्रेथिंग सांस ले श्वसन breathing liye एसआई सी si गेसेस गेस गैस gases मिक्स मीक्स मिश्रण mix ले ली le जा जत jate`
- tokens: diver→डाइवर (+डाइवर), underwater→अंडरवाटर (+जलमग्न), breathing→ब्रीथिंग (+सांस लेना/श्वसन), ke→-, liye→लिये, kaun→-, kaun→-, si→एसआई, gases→गेसेस (+गैस), ka→-, mix→मिक्स (+मिश्रण), le→ले, jate→जाते, hain→-
- top-3 retrieved: श्वसन तंत्र | प्रकाश-संश्लेषण | स्कूबा डाइविंग
- relevant: स्कूबा डाइविंग

## 475002#0 (mix50)
- native: अतिक्रमण विरोधी अभियान किस शहर में शुरू किया गया?
- query: `atikraman anti campaign which city mein start kiya gaya?`
- normalised: `अतिक्रमण अतिक्रमन atikraman अंत अन्त विरोध विरोध anti कैम्पेन कैंपेन अभियान campaign सिट सीट शहर city स्टार्ट स्टॉर्ट शुर स्टार्ट start कीय kiya गाय gaya`
- tokens: atikraman→अतिक्रमण, anti→अंति (+विरोधी/विरोध), campaign→कैम्पेन (+अभियान), city→सिटी (+शहर), mein→-, start→स्टार्ट (+शुरू/स्टार्ट), kiya→किया, gaya→गया
- top-3 retrieved: ऑपरेशन जंक्शन सिटी | एयर अस्ताना | सिटी ऑफ़ लंदन
- relevant: नक्सलवाद | नक्सलवाद

## 318934#0 (mix75)
- native: लैंगिक प्रजनन के दौरान जब अलग-अलग कोशिकाएं संयोजित होती है तो वे किसका निर्माण करती है?
- query: `sexual reproduction ke dauran jab different cells combine hoti hain to they kaun sa structure banati hain?`
- normalised: `सेक्सुअल सैक्सुअल यौन सेक्सुअल sexual रिप्रोडक्शन रीप्रोडक्शन प्रजनन reproduction दौरान दौरन dauran जाब jab डिफरेंट डिफ्रेंट विभिन्न भिन्न different सेल्स सैल्स कोशिक cells कम्बाइन कंबाइन मिल combine थेय they सा स sa स्ट्रक्चर स्ट्रकचर संरच रच structure बन बन banati`
- tokens: sexual→सेक्सुअल (+यौन/सेक्सुअल), reproduction→रिप्रोडक्शन (+प्रजनन), ke→-, dauran→दौरान, jab→जब, different→डिफरेंट (+विभिन्न/भिन्न), cells→सेल्स (+कोशिकाएँ), combine→कम्बाइन (+मिलाना), hoti→-, hain→-, they→थे (+वे/उन्हें), kaun→-, sa→सा, structure→स्ट्रक्चर (+संरचना/रचना), banati→बनती, hain→-
- top-3 retrieved: शैवाल | मल्टीपल माइलोमा | आनुवंशिकी
- relevant: प्राणी | कोशिका विभाजन | कोशिका विज्ञान

## 462672#0 (mix50)
- native: कौन सा खेल चार दीवारों से घिरे कोर्ट में खेला जाता है?
- query: `kaun sa sport chaar walls mein play hota hai?`
- normalised: `सा स sa स्पोर्ट स्पॉर्ट खेल स्पोर्ट sport चार छार chaar वॉल्स वाल्स दीवार walls प्ल प्लेय खेल play`
- tokens: kaun→-, sa→सा, sport→स्पोर्ट (+खेल/स्पोर्ट), chaar→चार, walls→वॉल्स (+दीवारें), mein→-, play→प्ले (+खेल), hota→-, hai→-
- top-3 retrieved: लिब्बी कोसमाला | अन्ना मिलेनिना | नरवाना
- relevant: स्क्वैश (खेल) | स्क्वैश (खेल) | स्क्वैश (खेल)

## 819444#0 (mix50)
- native: केरल के तट को क्या कहते हैं?
- query: `kerala ke coast ko kya called hain?`
- normalised: `केरल केरल kerala कोस्ट कॉस्ट तट coast कॉल्ड काल्ड कॉल called`
- tokens: kerala→केरला, ke→-, coast→कोस्ट (+तट), ko→-, kya→-, called→कॉल्ड (+कहा गया/कॉल किया), hain→-
- top-3 retrieved: अनानास | गोल्ड कोस्ट, क्वींसलैंड | केरल
- relevant: तिरुवनन्तपुरम | पश्चिमी तटीय मैदानी क्षेत्र | भारत में पर्यटन

## 229031#0 (mix75)
- native: भारत में सही मायने में किसे 'स्थानीय स्वशासन का जनक' कहा जाता?
- query: `india mein sahi maayne mein kis ko 'local self governance ka founder' called?`
- normalised: `इंड इंद भारत india साह सह sahi माय माय् maayne लोकल लोकाल स्थान local सेल्फ सेल्फ़ स्वय सेल्फ self गवर्नेंस गवर्नेन्स शासन governance फाउंडर फाउण्डर संस्थापक founder कॉल्ड काल्ड कॉल called`
- tokens: india→इंडिया (+भारत), mein→-, sahi→साही, maayne→मायने, mein→-, kis→-, ko→-, local→लोकल (+स्थानीय), self→सेल्फ (+स्वयं/सेल्फ), governance→गवर्नेंस (+शासन), ka→-, founder→फाउंडर (+संस्थापक), called→कॉल्ड (+कहा गया/कॉल किया)
- top-3 retrieved: इंटेल | संयुक्त राज्य अमेरिका में अमेरिकी मूल-निवासी | शियान एच-6
- relevant: पंचायती राज

## 13085#0 (mix75)
- native: सर्वाधिक बोले जाने वाली भाषा कौन-सी है?
- query: `most spoken language kaun-si?`
- normalised: `मोस्ट मॉस्ट most स्पोकेन स्पोकन बोल स्पोकन spoken लैंग्वेज लैंगुएज भाष language एसआई सी si`
- tokens: most→मोस्ट (+सबसे), spoken→स्पोकेन (+बोला/स्पोकन), language→लैंग्वेज (+भाषा), kaun→-, si→एसआई
- top-3 retrieved: न्यूयॉर्क शहर की जनसांख्यिकी | भाषा तकनीकी | विदेशी भाषा
- relevant: चीनी जनवादी गणराज्य | मन्दारिन भाषा

## 877082#0 (mix75)
- native: प्रदर्शन' प्रसार शिक्षा के जिन सिद्धान्तों को प्रतिपादित कौन करता है?
- query: `display dissemination education ke jin principles ko articulated kaun does hai?`
- normalised: `डिस्प्ल डिसप्ल प्रदर्श डिस्प्ल display डिसेमिनेशन डिसिमिनेशन प्रसार dissemination एड्यूकेशन एडुकेशन शिक्ष education जीन jin प्रिंसिपल्स प्रिन्सिपल्स सिद्धांत principles आर्टिकुलेटेड आर्टिक्युलेटेड व्यक्त articulated`
- tokens: display→डिस्प्ले (+प्रदर्शित/डिस्प्ले), dissemination→डिसेमिनेशन (+प्रसार), education→एड्यूकेशन (+शिक्षा), ke→-, jin→जिन, principles→प्रिंसिपल्स (+सिद्धांत), ko→-, articulated→आर्टिकुलेटेड (+व्यक्त किया), kaun→-, hai→-
- top-3 retrieved: कंप्यूटर डिस्प्ले | कंप्यूटर डिस्प्ले | डिस्प्ले डाटा चैनल
- relevant: विकास प्रशासन

#! /bin/bash 

# input paraameter
say="$1"
TARGET_LANG="$2"
if [ -z "$TARGET_LANG" ]; then TARGET_LANG="DE"; fi;
echo "TARGET_LANG $TARGET_LANG"


CONST_TARGET_LANGUAGE_DE="de-DE"
CONST_TARGET_VOICE_DE="de-DE-Neural2-B"
CONST_TARGET_GENDER_DE="MALE"

CONST_TARGET_LANGUAGE_FR="fr-FR"
CONST_TARGET_VOICE_FR="fr-FR-Wavenet-A"
CONST_TARGET_GENDER_FR="FEMALE"

CONST_TARGET_LANGUAGE_EN="en-GB"
CONST_TARGET_VOICE_EN="en-GB-Wavenet-B"
CONST_TARGET_GENDER_EN="MALE"

# check some basic prefereces
if [ ! -f /usr/bin/jq ]; then echo "Prerequisite Error: The command 'jq' must be installed"; fi;
export GOOGLE_APPLICATION_CREDENTIALS="/home/wepa/service-account-text2speech.json"
if [  ! -f  $GOOGLE_APPLICATION_CREDENTIALS ]; then echo "Prerequisite Error: Missing service-account-text2speech.json file"; fi;

# get main input

# default value for easier testing
if [ -z "$say" ]; then
		read -p "sprich ($say): $say " say
		if [ -z "$say" ]; then
			say="Hallo Sandra. Jetzt ist es also soweit. Die erste Version des Texteingabe- und Sprachausgabe-Programmes liegt vor. Ich hoffe, dass es uns dienen wird. "
		fi
fi

# code input for spelling correction (replace SPACE with +)
#say_enc=$(echo "$say" | tr " " +)

# call spelling API
# curl "https://api.textgears.com/correct?text=$say_enc&ai=1&language=de-CH&key=AvNwNand3KXVWe6Q" > corrected.txt
# say_corrected=$(cat corrected.txt | jq .response.corrected | sed 's/\"//g')

# code  language input
if [ "$TARGET_LANG" == "DE" ]
	then
		TARGET_LANGUAGE="$CONST_TARGET_LANGUAGE_DE"
		TARGET_VOICE="$CONST_TARGET_VOICE_DE"
		TARGET_GENDER="$CONST_TARGET_GENDER_DE"
elif [ "$TARGET_LANG" == "FR" ]
	then
		TARGET_LANGUAGE="$CONST_TARGET_LANGUAGE_FR"
		TARGET_VOICE="$CONST_TARGET_VOICE_FR"
		TARGET_GENDER="$CONST_TARGET_GENDER_FR"
elif [ "$TARGET_LANG" == "EN" ]
        then
                TARGET_LANGUAGE="$CONST_TARGET_LANGUAGE_EN"
                TARGET_VOICE="$CONST_TARGET_VOICE_EN"
                TARGET_GENDER="$CONST_TARGET_GENDER_EN"
fi

#echo "TARGET_LANGUAGG: $TARGET_LANGUAGE"
#echo "TARGET_VOICE: $TARGET_VOICE"
#echo "TARGET_GENDER: $TARGET_GENDER"

# if target_language is not DE then  translate the input into the target laguage.
if [ "$TARGET_LANG" !=  "DE" ]
	then
		curl -H "Content-Type: application/x-www-form-urlencoded" -d "key=AIzaSyAE8UUGK6q-brPLEEGUM8mfTDuCfHVHiec&q=$say&target=$TARGET_LANG&format=text&source=DE" https://translation.googleapis.com/language/translate/v2 > translated.txt
		say_translated=$(cat translated.txt | jq .data.translations[0].translatedText | sed 's/\"//g')
		#echo "FR:translated: $say_translated"

	else

		# use corrected value if no translation was needed
		say_translated="$say"
		#echo "DE:translated: $say_translated"

fi


# synthezise output

say_translated=$( echo $say_translated | sed "s/'/\\\'/g" )

curl -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) -H "Content-Type: application/json; charset=utf-8" --data "{ 'input':{ 'text':'$say_translated'}, 'voice':{ 'languageCode':'$TARGET_LANGUAGE', 'name':'$TARGET_VOICE', 'ssmlGender':'$TARGET_GENDER'},'audioConfig':{'audioEncoding':'LINEAR16'}}" "https://texttospeech.googleapis.com/v1/text:synthesize" > out.json
cat out.json |  jq --raw-output .audioContent | base64 --decode >  out.wav  && /usr/bin/paplay out.wav;

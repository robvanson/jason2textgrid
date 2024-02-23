#!python
# 
# Convert WhisperX time-stamped segments and words from JSON to praat TextGrids
# 
# Use:
# python json2textgrid file1 file2 ...
#
# Output:
# TextGrid files with extension "<filename>.TextGrid"
#
# Copyright: R.J.J.H. van Son, 2024
# 
# License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#
import glob
import sys
from pathlib import Path
from os.path import exists
import json
import re

sys.argv.pop(0)

file_list = sys.argv

fillerText = ""
for f in file_list:
	print(f)
	outfile = re.sub(r"\.json$", r"", f)
	outfile += ".TextGrid"
	jsontxt = Path(f).read_text()
	jsonobj = json.loads(jsontxt)
	textGrids = {}
	# Segments tier
	segmentsTier = []
	t_segments = 0
	t_last = 0
	for segm in jsonobj["segments"]:
		if segm['start'] > t_segments:
			segmentsTier.append([t_segments, segm['start'], fillerText])
			fillerText = ""
		segmentsTier.append([segm['start'],  segm['end'], segm['text'].strip()])
		t_segments = segm['end']
	if t_last < t_segments:
		t_last = t_segments
	# Add tier
	textGrids["segments"] = segmentsTier
	# Words tier
	wordsTier=[]
	scoreTier=[]
	t_words = 0
	for word in jsonobj["word_segments"]:
		if len(word) < 3:
			# Incomplete word element
			fillerText = word["word"]
			print(word)
		else:
			if word['start'] > t_words:
				wordsTier.append([t_words, word['start'], fillerText])
				fillerText = ""
				scoreTier.append([t_words, word['start'], ""])
			wordsTier.append([word['start'],  word['end'], word['word'].strip()])
			scoreTier.append([word['start'],  word['end'], word['score']])
			t_words = word['end']
	if t_last <= t_words:
		t_last = t_words
	else:
		wordsTier.append([t_words,  t_last, ''])
	# Add tiers
	textGrids["words"] = wordsTier
	textGrids["scores"] = scoreTier
	
	# Construct text
	textGridtext = 'File type = "ooTextFile"\n'
	textGridtext += 'Object class = "TextGrid"\n\n'
	textGridtext += '0\n'
	textGridtext +=  "{}".format(t_last) + '\n'
	textGridtext +=  '<exists>\n'
	textGridtext +=  "{}".format(len(textGrids.keys())) + '\n'
	for key in  textGrids.keys():
		textGridtext +=  '"IntervalTier"\n'
		textGridtext +=  '"{}"\n'.format(key)
		tierList = textGrids[key]
		textGridtext +=  '{}\n'.format(0)
		textGridtext +=  '{}\n'.format(t_last)
		textGridtext +=  '{}\n'.format(len(tierList))
		for e in tierList:
			textGridtext +=  '{}\n{}\n"{}"\n'.format(e[0], e[1], e[2])

	with open(outfile, 'w') as o:
		o.write(textGridtext)
	

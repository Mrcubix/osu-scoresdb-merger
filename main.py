import os
import merger
import serializer

actual_path = os.getcwd()
serializer.serialize_scoredb_data(merger.Merge_scores(actual_path + "\\input\\scores1.db", actual_path + "\\input\\scores.db"))

with open(r"./output/scores.db", "rb") as output:
    output_binary = str(output.read())

with open(r"D:\Program Files (x86)\osu!\scores.db", "rb") as model:
    model_binary = str(model.read())    

print(output_binary == model_binary)
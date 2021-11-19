from datetime import datetime
import re

sample = "stock-data-2.json"
object_oid = re.split("[.-]", sample)[2]
print(object_oid)
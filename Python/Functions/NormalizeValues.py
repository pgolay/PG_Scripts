def normalize_values(numList):
    maxVal = max(numList)
    return [d/maxVal for n in numList]
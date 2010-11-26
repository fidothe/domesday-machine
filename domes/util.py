def get_holding(placerefs):
    total = {}
    for ref in placerefs:
        if not ref.holding:
            continue
        if ref.units in total.keys():
            total[ref.units] += ref.holding
        else:
            total[ref.units] = ref.holding
    return total

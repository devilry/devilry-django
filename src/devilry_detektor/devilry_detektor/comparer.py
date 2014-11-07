import detektor


class DevilryDetektorCompareMany(detektor.comparer.CompareMany):
    def compare(self, parseresult1, parseresult2):
        if parseresult1.delivery.assignment_group == parseresult2.delivery.assignment_group:
            # Do not compare two deliveries by the same user
            return
        else:
            super(DevilryDetektorCompareMany, self).compare(parseresult1, parseresult2)

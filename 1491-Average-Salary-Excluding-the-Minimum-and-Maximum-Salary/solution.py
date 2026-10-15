class Solution:
    def average(self, salary: list[int]) -> float:
        for i in range(len(salary)-1):
            min_index = i
            for j in range(i+1,len(salary)):
                if salary[j] < salary[min_index]:
                    min_index = j
            
            salary[i],salary[min_index] = salary[min_index], salary[i]

        total = 0
        for i in range(1,len(salary)-1):
            total +=  salary[i]
        return total / (len(salary)-2)
        
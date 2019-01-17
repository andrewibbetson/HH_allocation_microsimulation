import uuid
import random

rd = random.Random()
rd.seed(0)


class HH(object):


    def __init__(self, hhsize, sexhrp, agehrp, dwtype, hhtype):
        
        self.id = str(uuid.UUID(int=rd.getrandbits(128))).split("-")[0]
        self.agehrp=agehrp
        self.sexhrp=sexhrp - 1 ## 0 male 1 female
        self.dwtype = dwtype
        self.hhtype= hhtype
        self.hhsize= hhsize
        self.occupants = []

        # for mixed integer programming
        # categories: seven categories of age, two for sex
        # [0] = 0,1 / [1] = 1,1 / [2] = 2,1 / [3] = 3,1 / [4] = 4,1 / [5] = 5,1 / [6] = 6,2 | [7] = 0,2 / [8] = 1,2 / [9] = 2,2 / [10] = 3,2 / [11] = 4,2 / [12] = 5,2 / [13] = 6,2

        self.mip = [0]*14


        if self.hhtype == 2:

            # couple
            if self.sexhrp == 0:
                self.mip[self.agehrp + 7] = 1
            else:
                self.mip[self.agehrp] = 1


            # children
            num_children = self.hhsize - 2
            sex_split_1 = int(num_children/2)
            sex_split_2 = num_children - sex_split_1
            random_choice = random.choice([True, False])

            if random_choice == True:
                self.mip[0] += sex_split_1
                self.mip[7] += sex_split_2
            else:
                self.mip[0] += sex_split_2
                self.mip[7] += sex_split_1


        elif self.hhtype == 1:


            # couple
            if self.sexhrp == 0:
                self.mip[self.agehrp + 7] = 1
            else:
                self.mip[self.agehrp] = 1

            # non-dependent children or elderly family memnber or lodger
            # for now assume young non-dependent children
            if self.hhsize > 2:

                num_persons = self.hhsize - 2
                sex_split_1 = int(num_persons/2)
                sex_split_2 = num_persons - sex_split_1
                random_choice = random.choice([True, False])

                if random_choice == True:
                    self.mip[1] += sex_split_1
                    self.mip[8] += sex_split_2
                else:
                    self.mip[1] += sex_split_2
                    self.mip[8] += sex_split_1



        elif self.hhtype == 3:

            # children
            num_children = self.hhsize - 1
            sex_split_1 = int(num_children/2)
            sex_split_2 = num_children - sex_split_1
            random_choice = random.choice([True, False])

            if random_choice == True:
                self.mip[0] += sex_split_1
                self.mip[7] += sex_split_2
            else:
                self.mip[0] += sex_split_2
                self.mip[7] += sex_split_1


        elif self.hhtype == 4:


            # multi-person gender split - assume equal M:F
            num_persons = self.hhsize - 1
            sex_split_1 = int(num_persons/2)
            sex_split_2 = num_persons - sex_split_1
            random_choice = random.choice([True, False])

            if random_choice == True:
                self.mip[self.agehrp] += sex_split_1
                self.mip[self.agehrp + 7] += sex_split_2
            else:
                self.mip[self.agehrp] += sex_split_2
                self.mip[self.agehrp + 7] += sex_split_1

import re


class Classifications:
    @staticmethod
    def get_full_classification_from_abbreviation(classification):
        """
        Returns the label of the provided classification
        :param classification: abbreviation of a classification (b/lb/vus/lp/p)
        :return: the label of the classification
        """
        class_map = {'lb': 'Likely benign', 'b': 'Benign', 'lp': 'Likely pathogenic', 'p': 'Pathogenic', 'vus': 'VUS'}
        return class_map[classification]

    @staticmethod
    def transform_classification(lab_classification):
        """Transforms the 5-tier classification of the lab into a 3-tier consensus classification
         :param lab_classification: classification of the lab
         :return: the consensus classification
         """
        benign = '(Likely) benign'
        pathogenic = '(Likely) pathogenic'
        class_map = {'b': benign, 'p': pathogenic, 'lp': pathogenic, 'lb': benign, 'vus': 'VUS'}
        return class_map[lab_classification]

    @staticmethod
    def get_abbreviation_from_classification(classification):
        """
        Converts classifications (either 3-tier or 5-tier) into their ids
        :param classification: the classification to convert
        :return: the converted classification
        """
        classifications = {'benign': 'LB', 'vus': 'VUS', 'pathogenic': 'LP'}
        stripped_class = re.sub(r'\(?likely\)? ', '', classification.lower())
        return classifications[stripped_class]

    @staticmethod
    def is_conflicting_classification(classifications):
        """
        Determines whether classification is conflicting
        Conflicting if:
            [(likely) benign in classifications > 0]
            AND
            [(likely) pathogenic in classifications > 0]
        :param classifications: dictionary with all classifications and how many times they were seen for this variant
        :return: True if the classifications are conflicting and False if the classifications are not conflicting
        """
        return (classifications['b'] > 0 or classifications['lb'] > 0) and (
                classifications['lp'] > 0 or classifications['p'] > 0)

    @staticmethod
    def is_no_consensus(classifications):
        """
        Determines whether classifications are in disagreement
        No consensus if:
            [vus in classifications > 0]
            AND
            [lb/b/p/lp in classifications > 0]
        :param classifications: dictionary with all classifications and how many times they were seen for this variant
        :return: True if the classifications are not in agreement and False if the classifications are in agreement
        """
        return classifications['vus'] > 0 and (
                classifications['lb'] > 0 or classifications['b'] > 0 or classifications['lp'] > 0 or
                classifications['p'] > 0)

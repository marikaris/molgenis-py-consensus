from consensus.Classifications import Classifications

import progressbar


class ConsensusTableGenerator:
    """
    The ConsensusTableGenerator generates the a dictionary with all unique variants, their classifications by the labs
    and whether the labs agree upon the classifications
    """

    def __init__(self, lab_data):
        """
        :param lab_data: lab data as generated by DataRetriever ({lab1: [{variant1}, {variant2}, ...], lab2: [...]})
        """
        self.lab_data = lab_data
        self.labs = [lab for lab in lab_data]
        self.all_variants = {}
        self.all_classifications = {}
        self.all_lab_classifications = {}
        self.no_consensus = 'No consensus'
        self.opposite_consensus = 'Opposite classifications'

    def _add_new_variant(self, variant_id, variant, lab):
        """
        Adds a new unique variant to the all_variants dictionary
        :param variant_id: the id of the variant (chr_pos_ref_alt_gene)
        :param variant: the variant as specified by the lab
        :param lab: the lab that saw the variant
        :return: None
        """
        classifications = {'vus': 0, 'b': 0, 'lb': 0, 'p': 0, 'lp': 0}
        lab_classification = variant['classification']['id']
        classifications[lab_classification] += 1
        self.all_classifications[variant_id] = classifications
        self.all_variants[variant_id] = {
            'chromosome': variant['chromosome'],
            'start': variant['start'],
            'ref': variant['ref'],
            'alt': variant['alt'],
            'gene': variant['gene'],
            'type': variant['type'],
            lab + '_link': variant['id'],
            'id': variant_id,
            'consensus_classification': 'Classified by one lab'

        }
        self._update_if_not_exists('c_dna', variant, variant_id)
        self._update_if_not_exists('protein', variant, variant_id)
        if 'stop' in variant and variant['stop'] != "0":
            self._update_if_not_exists('stop', variant, variant_id)
        self._update_if_not_exists('transcript', variant, variant_id)

        self.all_lab_classifications[variant_id] = {lab: '' for lab in self.labs}

        self.all_lab_classifications[variant_id][lab] = variant['classification']['id']

    def _update_if_not_exists(self, element, variant, variant_id):
        """
        Updates the element of the variant if it is not specified yet
        :param element: the element to update
        :param variant: the variant as specified by the lab
        :param variant_id: the id of the variant in the consensus table (chr_pos_ref_alt_gene)
        :return: None
        """
        if element not in self.all_variants[variant_id] and element in variant:
            self.all_variants[variant_id][element] = variant[element]

    def _update_variant_classification(self, variant_id, variant, lab):
        """
        Updates a unique variant in the all_variants dictionary if it already exists
        :param variant_id: the id of the variant in the consensus table (chr_pos_ref_alt_gene)
        :param variant: the variant as specified by the lab
        :param lab: the id of the lab
        :return: None
        """
        classifications = self.all_classifications[variant_id]
        lab_class = variant['classification']['id']
        classifications[variant['classification']['id']] += 1
        self.all_variants[variant_id][lab + '_link'] = variant['id']
        current_consensus = self.all_variants[variant_id]['consensus_classification']

        self._update_if_not_exists('c_dna', variant, variant_id)
        self._update_if_not_exists('protein', variant, variant_id)

        if 'stop' in variant and variant['stop'] != "0":
            self._update_if_not_exists('stop', variant, variant_id)

        self._update_if_not_exists('transcript', variant, variant_id)
        self.all_lab_classifications[variant_id][lab] = variant['classification']['id']

        # No need to check if we already know the classification is opposite it will stay opposite
        if not current_consensus == self.opposite_consensus:
            # Conflicting should be checked first since it is a form of "no consensus" and wins over it
            if Classifications.is_conflicting_classification(classifications):
                self.all_variants[variant_id]['consensus_classification'] = self.opposite_consensus
            elif Classifications.is_no_consensus(classifications) or current_consensus == self.no_consensus:
                self.all_variants[variant_id]['consensus_classification'] = self.no_consensus
            else:
                # Checked if no consensus or opposite consensus, so we may assume the classifications are in agreement
                classification = Classifications.transform_classification(lab_class)
                self.all_variants[variant_id]['consensus_classification'] = classification

    def process_variants(self):
        """
        For each lab, for each variant, check if it exists in the all_variants,
        if not add new variant, else update variant with lab classification
        :return: all_variants ({chr_pos_ref_alt:{variant info}})
        """
        total_variants = sum([len(self.lab_data[lab]) for lab in self.lab_data])
        current = 0
        print('\nProcessing variants')
        new_progress = progressbar.ProgressBar(max_value=total_variants)
        for lab in self.lab_data:
            lab_variants = self.lab_data[lab]
            for variant in lab_variants:
                lab_id = lab.replace('_', '').upper() + '_'
                variant_id = variant['id'].replace(lab_id, '')
                if variant_id not in self.all_variants:
                    self._add_new_variant(variant_id, variant, lab)
                else:
                    self._update_variant_classification(variant_id, variant, lab)
                current += 1
                new_progress.update(current)
        new_progress.finish()
        return self.all_variants
export type Option = { value: number; label: string };

export type Question = {
  id: number;
  category_id: number;
  category_name: string;
  sub_index: number;
  sub_name?: string;
  question_text: string;
  scale_min: number;
  scale_max: number;
  option_labels_raw?: string;
  option_labels?: Option[];
  references_text?: string;
  source_links?: string;
};

export type GroupedCategory = {
  category_id: number;
  category_name: string;
  questions: Question[];
};

export type CategorySummary = {
  category_id: number;
  category_name: string;
  question_count: number;
};

export type Meta = { title?: string | null; subtitle?: string | null; };

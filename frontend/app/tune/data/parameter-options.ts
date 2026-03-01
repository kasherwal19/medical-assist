export const requiredGroups = [
  { title: 'Target Audience', required: true, options: ['Oncologist', 'General Physician', 'Pediatrician', 'Cardiologist', 'Nurse Practitioner', 'Patient/Parent', 'Pharmacist'] },
  { title: 'Tone', required: true, options: ['Scientific', 'Neutral', 'Empathetic', 'Conversational', 'Data-heavy', 'Patient-friendly', 'Technical'] },
  { title: 'Purpose', required: true, options: ['Commercial', 'Non-commercial', 'Scientific Communication', 'Patient Education', 'Clinical Education', 'Medical Awareness', 'Regulatory Summary'] },
  { title: 'Format', required: true, options: ['Short Summary', 'Long-form Article', 'Educational Note', 'FAQ Format', 'Slide Copy', 'Newsletter-Style', 'Social Post'] }
];

export const optionalGroups = [
  { title: 'Medical Depth', options: ['High-level overview', 'Moderately technical', 'Deep scientific detail', 'Mechanism-of-action heavy', 'Data/evidence-rich', 'Layperson-friendly'] },
  { title: 'Focus Area', options: ['Symptoms & Diagnosis', 'Prognosis & Risk Factors', 'Treatment Options', 'Safety & Adverse Effects', 'Drug Efficacy Data', 'Clinical Workflow / Practical Guidance', 'Patient Counselling Points', 'Preventive Care'] },
  { title: 'Reading Difficulty', options: ['Highly technical', 'Standard medical literacy', 'Easy-to-read', 'Parent/patient-friendly (5-6th grade level)'] },
  { title: 'Target Reading Time', options: ['1-min read', '3-min read', '7-min read'] }
];
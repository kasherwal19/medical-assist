'use client';

import { Suspense } from 'react';
import Header from '@/components/Header';
import Stepper from '@/components/Stepper';
import Image from 'next/image';
import Link from 'next/link';
import ParametersStep from '@/app/tune/components/ParametersStep';
import ImagesStep from '@/app/tune/components/ImageStep';
import TemplateStep from '@/app/tune/components/TemplateStep';
import { useContentTuning } from '@/app/tune/hooks/useContentTuning';

function ContentTuningInner() {
  const {
    currentStep,
    isGenerating,
    selections, setSelections,
    showOptional, setShowOptional,
    includeImages, setIncludeImages,
    allImages, isLoadingImages,
    selectedImageId, setSelectedImageId,
    selectedTemplate, setSelectedTemplate,
    handleBack,
    handleNext
  } = useContentTuning();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans relative overflow-hidden">
      {/* Background Gradient Mesh */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-100/40 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-teal-100/40 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10">
        <Header />
      </div>

      <main className="relative z-10 max-w-5xl mx-auto px-6 py-8 animate-fadeIn">
        <div className="mb-8 flex justify-between items-start">
          <div>
            <button onClick={handleBack} className="inline-flex items-center text-accent1 text-sm font-medium hover:underline gap-2 cursor-pointer transition-colors mb-6 appearance-none bg-transparent outline-none border-none">
              <div className="bg-white p-1 rounded-full border border-slate-200 block text-xs shadow-sm">
                <Image src="/icons/arrow-left.svg" alt="Back" width={14} height={14} className="opacity-70" />
              </div>
              <span className="block mt-0.5">Go Back</span>
            </button>
            <h1 className="text-3xl font-semibold text-slate-800 tracking-tight">Tune Content Parameters</h1>
            <p className="text-slate-500 mt-2 text-base">Configure the generation settings for your selected documents.</p>
          </div>
        </div>

        <Stepper currentStep={currentStep} />

        <div className="glass-panel bg-white p-8 rounded-2xl min-h-[500px] shadow-sm border border-slate-200 mt-8 flex flex-col">
          {currentStep === 1 && (
            <ParametersStep
              selections={selections}
              setSelections={setSelections}
              showOptional={showOptional}
              setShowOptional={setShowOptional}
              includeImages={includeImages}
              setIncludeImages={setIncludeImages}
              onNext={handleNext}
            />
          )}

          {currentStep === 2 && (
            <ImagesStep
              allImages={allImages}
              isLoadingImages={isLoadingImages}
              selectedImageId={selectedImageId}
              setSelectedImageId={setSelectedImageId}
              onNext={handleNext}
            />
          )}

          {currentStep === 3 && (
            <TemplateStep
              selectedTemplate={selectedTemplate}
              setSelectedTemplate={setSelectedTemplate}
              includeImages={includeImages}
              onNext={handleNext}
              isGenerating={isGenerating}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default function ContentTuning() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center">Loading Content Tuning...</div>}>
      <ContentTuningInner />
    </Suspense>
  );
}
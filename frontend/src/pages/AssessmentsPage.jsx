import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assessmentsApi, episodesApi } from '../api/client';
import {
  GraduationCap,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Trophy,
  RotateCcw,
  ArrowLeft,
  Loader2,
  Code2,
  MessageSquare,
  ListChecks,
  Sparkles,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function scoreColor(score) {
  if (score >= 80) return 'text-green-400';
  if (score >= 60) return 'text-yellow-400';
  return 'text-red-400';
}

function scoreBadgeColor(score) {
  if (score >= 80) return 'bg-green-500/20 text-green-400';
  if (score >= 60) return 'bg-yellow-500/20 text-yellow-400';
  return 'bg-red-500/20 text-red-400';
}

function scoreBgRing(score) {
  if (score >= 80) return 'ring-green-500/50';
  if (score >= 60) return 'ring-yellow-500/50';
  return 'ring-red-500/50';
}

function difficultyBadge(d) {
  switch (d) {
    case 'easy':
      return 'bg-green-500/20 text-green-400';
    case 'medium':
      return 'bg-yellow-500/20 text-yellow-400';
    case 'hard':
      return 'bg-red-500/20 text-red-400';
    default:
      return 'bg-gray-500/20 text-gray-400';
  }
}

function ProgressBar({ percent, className = '' }) {
  return (
    <div className={`h-2 bg-gray-800 rounded-full overflow-hidden ${className}`}>
      <div
        className="h-full rounded-full bg-blue-500 transition-all duration-500"
        style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
      />
    </div>
  );
}

function ConfettiEffect() {
  const particles = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    delay: Math.random() * 2,
    duration: 2 + Math.random() * 2,
    color: ['#3b82f6', '#22c55e', '#eab308', '#ec4899', '#a855f7', '#06b6d4'][i % 6],
  }));
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute w-2 h-2 rounded-full animate-confetti"
          style={{
            left: `${p.left}%`,
            backgroundColor: p.color,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        />
      ))}
      <style>{`
        @keyframes confetti {
          0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
          100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
        }
        .animate-confetti { animation: confetti linear forwards; }
      `}</style>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MODE 1: Quiz Selection
// ---------------------------------------------------------------------------

function QuizSelectionView({ onStartQuiz }) {
  const [history, setHistory] = useState([]);
  const [episodes, setEpisodes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetch() {
      try {
        const [historyRes, episodesRes] = await Promise.all([
          assessmentsApi.getHistory(),
          episodesApi.getAll(),
        ]);
        setHistory(Array.isArray(historyRes.data) ? historyRes.data : []);
        setEpisodes(Array.isArray(episodesRes.data) ? episodesRes.data : []);
      } catch (err) {
        console.error('Failed to load assessments:', err);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, []);

  // Build list of episodes that have assessments
  const assessed = episodes.filter((ep) => ep.has_assessment);

  // Merge history scores into episodes
  const scoreMap = {};
  history.forEach((h) => {
    scoreMap[h.episode_num] = h.score;
  });

  // Group by phase
  const byPhase = {};
  assessed.forEach((ep) => {
    const phase = ep.phase ?? 1;
    if (!byPhase[phase]) byPhase[phase] = [];
    byPhase[phase].push(ep);
  });
  const sortedPhases = Object.keys(byPhase)
    .map(Number)
    .sort((a, b) => a - b);

  // Overall stats
  const scoredEntries = history.filter((h) => h.score != null);
  const avgScore =
    scoredEntries.length > 0
      ? Math.round((scoredEntries.reduce((s, h) => s + h.score, 0) / scoredEntries.length) * 100)
      : 0;
  const totalAnswered = scoredEntries.length;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Assessments</h1>
        <div className="flex flex-wrap items-center gap-4 mt-2 text-sm text-gray-400">
          <span>
            Average Score:{' '}
            <span className={`font-semibold ${avgScore > 0 ? scoreColor(avgScore) : 'text-gray-500'}`}>
              {avgScore}%
            </span>
          </span>
          <span>
            Total Quizzes Taken: <span className="font-semibold text-gray-200">{totalAnswered}</span>
          </span>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-900 border border-gray-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : assessed.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
          <GraduationCap size={48} className="mb-4 text-gray-700" />
          <p className="text-lg font-medium text-gray-400">
            No assessments available yet. Generate episodes with assessments first.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {sortedPhases.map((phase) => (
            <div key={phase}>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Phase {phase}
              </h2>
              <div className="space-y-2">
                {byPhase[phase]
                  .sort((a, b) => (a.episode_num ?? a.id) - (b.episode_num ?? b.id))
                  .map((ep) => {
                    const epNum = ep.episode_num ?? ep.id;
                    const rawScore = scoreMap[epNum] ?? ep.assessment_score;
                    const hasTaken = rawScore != null;
                    const pct = hasTaken ? Math.round(rawScore * 100) : null;

                    return (
                      <div
                        key={epNum}
                        className="flex items-center justify-between bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 hover:border-gray-700 transition-colors"
                      >
                        <div className="flex items-center gap-4 min-w-0">
                          <span className="text-sm font-mono text-gray-500 w-10 shrink-0">
                            #{String(epNum).padStart(3, '0')}
                          </span>
                          <div className="min-w-0">
                            <p className="font-medium text-gray-200 truncate">
                              {ep.topic_name ?? ep.topic ?? 'Untitled'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          {hasTaken && (
                            <span
                              className={`text-xs px-2.5 py-1 rounded-full font-medium ${scoreBadgeColor(pct)}`}
                            >
                              {pct}%
                            </span>
                          )}
                          <button
                            onClick={() => onStartQuiz(epNum)}
                            className={`text-xs font-medium px-4 py-2 rounded-lg transition-colors ${
                              hasTaken
                                ? 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white'
                                : 'bg-blue-500 hover:bg-blue-600 text-white'
                            }`}
                          >
                            {hasTaken ? 'Retake' : 'Take Quiz'}
                          </button>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// MODE 2: Active Quiz
// ---------------------------------------------------------------------------

function ActiveQuizView({ episodeNum, onBack }) {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({}); // { questionId: userAnswer }
  const [results, setResults] = useState({}); // { questionId: AssessmentResult }
  const [submitting, setSubmitting] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    async function fetch() {
      try {
        const res = await assessmentsApi.get(episodeNum);
        setAssessment(res.data);
      } catch (err) {
        console.error('Failed to load assessment:', err);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, [episodeNum]);

  const questions = assessment?.questions ?? [];
  const currentQ = questions[currentIdx];
  const totalQ = questions.length;
  const answeredCount = Object.keys(results).length;
  const correctCount = Object.values(results).filter((r) => r.is_correct).length;
  const allAnswered = answeredCount === totalQ && totalQ > 0;
  const currentResult = currentQ ? results[currentQ.id] : null;

  // Reset selected option / text when navigating questions
  useEffect(() => {
    if (currentQ) {
      const prev = answers[currentQ.id];
      if (currentQ.question_type === 'multiple_choice') {
        setSelectedOption(prev ?? null);
      } else {
        setTextInput(prev ?? '');
      }
    }
  }, [currentIdx, currentQ?.id]);

  const handleSubmitAnswer = useCallback(async () => {
    if (!currentQ || submitting) return;

    const userAnswer =
      currentQ.question_type === 'multiple_choice' ? selectedOption : textInput.trim();
    if (!userAnswer) return;

    setAnswers((prev) => ({ ...prev, [currentQ.id]: userAnswer }));
    setSubmitting(true);

    try {
      const res = await assessmentsApi.submit(episodeNum, {
        assessment_id: currentQ.id,
        user_answer: userAnswer,
      });
      setResults((prev) => ({ ...prev, [currentQ.id]: res.data }));
    } catch (err) {
      console.error('Submit error:', err);
    } finally {
      setSubmitting(false);
    }
  }, [currentQ, selectedOption, textInput, episodeNum, submitting]);

  // Self-grading for short_answer / code_challenge
  function handleSelfGrade(isCorrect) {
    if (!currentQ) return;
    setResults((prev) => ({
      ...prev,
      [currentQ.id]: { ...prev[currentQ.id], is_correct: isCorrect },
    }));
  }

  function goTo(idx) {
    if (idx >= 0 && idx < totalQ) setCurrentIdx(idx);
  }

  function handleFinish() {
    setShowResults(true);
  }

  // ---------------------------
  // Results Screen
  // ---------------------------
  if (showResults) {
    const pct = totalQ > 0 ? Math.round((correctCount / totalQ) * 100) : 0;

    // Breakdown by difficulty
    const byDifficulty = { easy: { total: 0, correct: 0 }, medium: { total: 0, correct: 0 }, hard: { total: 0, correct: 0 } };
    questions.forEach((q) => {
      const d = q.difficulty || 'medium';
      if (byDifficulty[d]) {
        byDifficulty[d].total++;
        if (results[q.id]?.is_correct) byDifficulty[d].correct++;
      }
    });

    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
        {pct >= 90 && <ConfettiEffect />}

        <div className="max-w-2xl mx-auto">
          {/* Score display */}
          <div className="text-center py-12">
            <div
              className={`inline-flex items-center justify-center w-32 h-32 rounded-full ring-4 ${scoreBgRing(pct)} mb-6`}
            >
              <div>
                <p className={`text-4xl font-bold ${scoreColor(pct)}`}>{pct}%</p>
                <p className="text-sm text-gray-400">
                  {correctCount}/{totalQ}
                </p>
              </div>
            </div>
            <h2 className="text-2xl font-bold mb-2">
              {pct >= 90
                ? 'Outstanding!'
                : pct >= 80
                ? 'Great job!'
                : pct >= 60
                ? 'Good effort!'
                : 'Keep studying!'}
            </h2>
            <p className="text-gray-400">
              Episode {episodeNum}: {assessment?.topic_name}
            </p>
          </div>

          {/* Difficulty breakdown */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
              Breakdown by Difficulty
            </h3>
            <div className="grid grid-cols-3 gap-4">
              {['easy', 'medium', 'hard'].map((d) => {
                const { total, correct } = byDifficulty[d];
                const dPct = total > 0 ? Math.round((correct / total) * 100) : 0;
                return (
                  <div key={d} className="text-center">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${difficultyBadge(d)}`}>
                      {d}
                    </span>
                    <p className={`text-2xl font-bold mt-2 ${total > 0 ? scoreColor(dPct) : 'text-gray-600'}`}>
                      {total > 0 ? `${dPct}%` : '—'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {correct}/{total}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={() => {
                setShowResults(false);
                setCurrentIdx(0);
              }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors text-sm font-medium"
            >
              <RotateCcw size={16} />
              Review Answers
            </button>
            <button
              onClick={onBack}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-500 hover:bg-blue-600 text-white transition-colors text-sm font-medium"
            >
              <ArrowLeft size={16} />
              Back to Assessments
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------
  // Loading
  // ---------------------------
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-blue-500" />
      </div>
    );
  }

  if (!assessment || totalQ === 0) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
          <GraduationCap size={48} className="mb-4 text-gray-700" />
          <p className="text-lg font-medium text-gray-400">
            No assessment found for Episode {episodeNum}.
          </p>
        </div>
      </div>
    );
  }

  // ---------------------------
  // Quiz UI
  // ---------------------------
  const progressPct = totalQ > 0 ? (answeredCount / totalQ) * 100 : 0;
  const typeIcon =
    currentQ.question_type === 'code_challenge'
      ? Code2
      : currentQ.question_type === 'short_answer'
      ? MessageSquare
      : ListChecks;
  const TypeIcon = typeIcon;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6 lg:p-8">
      {/* Quiz header */}
      <div className="max-w-3xl mx-auto">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors text-sm"
        >
          <ArrowLeft size={16} />
          Back to Assessments
        </button>

        <div className="mb-6">
          <h1 className="text-xl font-bold mb-1">
            Episode {episodeNum}: {assessment.topic_name}
          </h1>
          <div className="flex items-center justify-between text-sm text-gray-400 mb-2">
            <span>
              Question {currentIdx + 1} of {totalQ}
            </span>
            <span>
              {answeredCount}/{totalQ} answered
            </span>
          </div>
          <ProgressBar percent={progressPct} />
        </div>

        {/* Question card */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
          {/* Question meta */}
          <div className="flex items-center gap-2 mb-4">
            <TypeIcon size={14} className="text-gray-500" />
            <span className="text-xs text-gray-500 capitalize">{currentQ.question_type.replace(/_/g, ' ')}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${difficultyBadge(currentQ.difficulty)}`}>
              {currentQ.difficulty}
            </span>
          </div>

          {/* Question text */}
          <p className="text-lg font-medium text-gray-100 mb-6">{currentQ.question_text}</p>

          {/* ---- Multiple choice ---- */}
          {currentQ.question_type === 'multiple_choice' && (
            <div className="space-y-3">
              {(currentQ.options ?? []).map((opt, i) => {
                const letter = String.fromCharCode(65 + i);
                const isSelected = selectedOption === opt;
                const isSubmitted = !!currentResult;
                const isCorrect = isSubmitted && currentResult.correct_answer === opt;
                const isWrong = isSubmitted && isSelected && !currentResult.is_correct && currentResult.correct_answer !== opt;

                let btnClass = 'bg-gray-800 hover:bg-gray-700 border-gray-700';
                if (isSubmitted && isCorrect) {
                  btnClass = 'bg-green-500/10 border-green-500/50 text-green-300';
                } else if (isSubmitted && isWrong) {
                  btnClass = 'bg-red-500/10 border-red-500/50 text-red-300';
                } else if (isSelected && !isSubmitted) {
                  btnClass = 'bg-blue-500/10 border-blue-500/50 text-blue-300';
                }

                return (
                  <button
                    key={i}
                    onClick={() => !isSubmitted && setSelectedOption(opt)}
                    disabled={isSubmitted}
                    className={`w-full text-left p-4 rounded-lg border transition-colors flex items-start gap-3 ${btnClass} disabled:cursor-default`}
                  >
                    <span className="w-7 h-7 rounded-full border border-current flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                      {letter}
                    </span>
                    <span className="text-sm">{opt}</span>
                    {isSubmitted && isCorrect && <CheckCircle2 size={18} className="ml-auto text-green-400 shrink-0 mt-0.5" />}
                    {isSubmitted && isWrong && <XCircle size={18} className="ml-auto text-red-400 shrink-0 mt-0.5" />}
                  </button>
                );
              })}
            </div>
          )}

          {/* ---- Short answer ---- */}
          {currentQ.question_type === 'short_answer' && (
            <div>
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                disabled={!!currentResult}
                placeholder="Type your answer..."
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500/50 transition-colors disabled:opacity-60"
              />
            </div>
          )}

          {/* ---- Code challenge ---- */}
          {currentQ.question_type === 'code_challenge' && (
            <div>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                disabled={!!currentResult}
                placeholder="Write your code here..."
                rows={8}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-200 placeholder-gray-600 font-mono focus:outline-none focus:border-blue-500/50 transition-colors disabled:opacity-60 resize-y"
              />
            </div>
          )}

          {/* Submit button */}
          {!currentResult && (
            <button
              onClick={handleSubmitAnswer}
              disabled={
                submitting ||
                (currentQ.question_type === 'multiple_choice' ? !selectedOption : !textInput.trim())
              }
              className="mt-4 flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-500 hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed text-white font-medium text-sm transition-colors"
            >
              {submitting ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
              Submit Answer
            </button>
          )}

          {/* Result feedback */}
          {currentResult && (
            <div className="mt-5 space-y-3">
              {/* Correct / Incorrect banner */}
              <div
                className={`flex items-center gap-2 p-3 rounded-lg text-sm font-medium ${
                  currentResult.is_correct
                    ? 'bg-green-500/10 text-green-400'
                    : 'bg-red-500/10 text-red-400'
                }`}
              >
                {currentResult.is_correct ? (
                  <CheckCircle2 size={18} />
                ) : (
                  <XCircle size={18} />
                )}
                {currentResult.is_correct ? 'Correct!' : 'Incorrect'}
              </div>

              {/* Correct answer display for non-MC */}
              {currentQ.question_type !== 'multiple_choice' && (
                <div className="bg-gray-800 rounded-lg p-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                    Correct Answer
                  </p>
                  <pre className="text-sm text-gray-200 whitespace-pre-wrap font-mono">
                    {currentResult.correct_answer}
                  </pre>
                </div>
              )}

              {/* Self-grading for short answer / code challenge */}
              {(currentQ.question_type === 'short_answer' || currentQ.question_type === 'code_challenge') &&
                currentResult.is_correct === false && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">Self-grade:</span>
                    <button
                      onClick={() => handleSelfGrade(true)}
                      className="text-xs px-3 py-1.5 rounded-lg bg-green-500/20 hover:bg-green-500/30 text-green-400 transition-colors font-medium"
                    >
                      I got it right
                    </button>
                    <button
                      onClick={() => handleSelfGrade(false)}
                      className="text-xs px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 transition-colors font-medium"
                    >
                      I got it wrong
                    </button>
                  </div>
                )}

              {/* Explanation */}
              {currentResult.explanation && (
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                    Explanation
                  </p>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{currentResult.explanation}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Question indicators */}
        <div className="flex flex-wrap items-center justify-center gap-1.5 mb-6">
          {questions.map((q, i) => {
            const r = results[q.id];
            let dotClass = 'bg-gray-800 text-gray-500';
            if (i === currentIdx) {
              dotClass = 'bg-blue-500 text-white ring-2 ring-blue-500/50';
            } else if (r) {
              dotClass = r.is_correct
                ? 'bg-green-500/20 text-green-400'
                : 'bg-red-500/20 text-red-400';
            }
            return (
              <button
                key={q.id}
                onClick={() => goTo(i)}
                className={`w-8 h-8 rounded-full text-xs font-medium transition-colors ${dotClass}`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => goTo(currentIdx - 1)}
            disabled={currentIdx === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
          >
            <ChevronLeft size={16} />
            Previous
          </button>

          {allAnswered ? (
            <button
              onClick={handleFinish}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-medium text-sm transition-colors"
            >
              <Trophy size={16} />
              Finish Quiz
            </button>
          ) : (
            <button
              onClick={() => goTo(currentIdx + 1)}
              disabled={currentIdx === totalQ - 1}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
            >
              Next
              <ChevronRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

export default function AssessmentsPage() {
  const { episode_num } = useParams();
  const navigate = useNavigate();

  if (episode_num) {
    return (
      <ActiveQuizView
        episodeNum={parseInt(episode_num, 10)}
        onBack={() => navigate('/assessments')}
      />
    );
  }

  return <QuizSelectionView onStartQuiz={(num) => navigate(`/assessments/${num}`)} />;
}

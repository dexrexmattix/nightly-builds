import { scoutConfig } from './scoutConfig';
import { ScoutAgent } from './scoutAgent';

async function runComparativeTest() {
  const testPrompt = `Explain the benefits of using a cheaper OpenAI-compatible model for high-volume agent calls.`;

  console.log('Starting comparative test between Gemini Flash and z.ai GLM-4.7-Flash...\n');

  // Gemini Flash agent
  const geminiProfile = scoutConfig.authProfiles['gemini:flash'];
  const geminiAgent = new ScoutAgent(geminiProfile);

  // z.ai GLM-4.7-Flash agent
  const zaiProfile = scoutConfig.authProfiles['zai:manual'];
  const zaiAgent = new ScoutAgent(zaiProfile);

  try {
    console.log('Querying Gemini Flash model...');
    const geminiResult = await geminiAgent.query(testPrompt);
    console.log('Gemini Flash output:\n', geminiResult.output);
    console.log(`Gemini Flash cost: $${geminiResult.cost.toFixed(6)}\n`);

    console.log('Querying z.ai GLM-4.7-Flash model...');
    const zaiResult = await zaiAgent.query(testPrompt);
    console.log('z.ai GLM-4.7-Flash output:\n', zaiResult.output);
    console.log(`z.ai GLM-4.7-Flash cost: $${zaiResult.cost.toFixed(6)}\n`);

    // Basic output quality comparison (length and similarity)
    const geminiLength = geminiResult.output.length;
    const zaiLength = zaiResult.output.length;

    console.log('Output length comparison:');
    console.log(`Gemini Flash output length: ${geminiLength}`);
    console.log(`z.ai GLM-4.7-Flash output length: ${zaiLength}`);

    // Simple similarity check: number of common words
    const geminiWords = new Set(geminiResult.output.toLowerCase().split(/\W+/));
    const zaiWords = new Set(zaiResult.output.toLowerCase().split(/\W+/));
    const commonWords = [...geminiWords].filter(w => zaiWords.has(w) && w.length > 3);

    console.log(`Common words (length > 3): ${commonWords.length}`);
    console.log('Sample common words:', commonWords.slice(0, 10).join(', '));

    console.log('\nComparative test completed.');
  } catch (err) {
    console.error('Error during comparative test:', err);
  }
}

runComparativeTest();
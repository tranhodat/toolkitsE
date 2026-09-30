module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const redisUrl = process.env.UPSTASH_REDIS_REST_URL
    || process.env.KV_REST_API_URL
    || process.env.storage_KV_REST_API_URL
    || process.env.storage_REST_API_URL;
  const redisToken = process.env.UPSTASH_REDIS_REST_TOKEN
    || process.env.KV_REST_API_TOKEN
    || process.env.storage_KV_REST_API_TOKEN
    || process.env.storage_REST_API_TOKEN;
  if (!redisUrl || !redisToken) {
    return res.status(503).json({ error: 'Visit counter storage is not configured' });
  }

  try {
    const dateParts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Ho_Chi_Minh',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).formatToParts(new Date()).reduce((parts, part) => {
      if (part.type !== 'literal') parts[part.type] = part.value;
      return parts;
    }, {});
    const day = `${dateParts.year}-${dateParts.month}-${dateParts.day}`;
    const month = `${dateParts.year}-${dateParts.month}`;
    const redisEndpoint = redisUrl.replace(/\/$/, '');

    const response = await fetch(`${redisEndpoint}/pipeline`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${redisToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify([
        ['INCR', `vlute:visits:day:${day}`],
        ['INCR', `vlute:visits:month:${month}`],
      ]),
    });

    if (!response.ok) throw new Error(`Redis returned ${response.status}`);
    const results = await response.json();
    if (!Array.isArray(results) || results.length !== 2 || results.some((item) => item.error)) {
      throw new Error('Unexpected Redis response');
    }

    return res.status(200).json({
      today: Number(results[0].result),
      month: Number(results[1].result),
    });
  } catch (error) {
    console.error('Visit counter request failed:', error);
    return res.status(502).json({ error: 'Unable to update visit statistics' });
  }
};

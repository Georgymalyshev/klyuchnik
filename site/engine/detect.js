function shannonEntropy(text) {
  const counts = {};
  for (const c of text) {
    counts[c] = (counts[c] || 0) + 1;
  }
  let entropy = 0;
  for (const c in counts) {
    const p = counts[c] / text.length;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

function klyuchnikScan(text) {
  const found = [];
  const lower = text.toLowerCase();

  for (const rule of KLYUCHNIK_RULES) {
    if (rule.keywords.length > 0) {
      let hasKeyword = false;
      for (const k of rule.keywords) {
        if (lower.includes(k)) hasKeyword = true;
      }
      if (!hasKeyword) continue;
    }

    const re = new RegExp(rule.pattern, rule.flags);
    let m;
    while ((m = re.exec(text)) !== null) {
      if (m[0].length === 0) {
        re.lastIndex++;
        continue;
      }
      const secret = m[rule.group] !== undefined ? m[rule.group] : m[0];
      if (rule.entropy > 0 && shannonEntropy(secret) <= rule.entropy) continue;

      const check = KLYUCHNIK_CHECKS[rule.id];
      if (check && !check(secret)) continue;

      found.push({
        rule: rule.id,
        description: rule.description,
        secret: secret,
        start: m.index + m[0].indexOf(secret),
        warn: rule.warn,
      });
    }
  }
  return found;
}

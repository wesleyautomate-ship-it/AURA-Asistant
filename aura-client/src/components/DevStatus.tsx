import { useEffect, useState } from 'react';
import { fetchHealth, fetchVersion } from '../api/dev';

export default function DevStatus() {
  const [ok, setOk] = useState<boolean | null>(null);
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      const [healthOk, ver] = await Promise.all([fetchHealth(), fetchVersion()]);
      if (!mounted) return;
      setOk(healthOk);
      setVersion(ver);
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const healthText = ok === null ? '...' : ok ? 'API OK' : 'API Down';
  const versionText = version ?? '...';

  return (
    <div className="px-3 py-1 text-[11px] text-gray-500 select-none">
      {healthText}  Version {versionText}
    </div>
  );
}


interface Props {
  files: File[];
  useDefaults: boolean;
  onFilesChange: (files: File[]) => void;
  onUseDefaultsChange: (use: boolean) => void;
}

export function PolicyUpload({
  files,
  useDefaults,
  onFilesChange,
  onUseDefaultsChange,
}: Props) {
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (useDefaults) return;
    const dropped = Array.from(e.dataTransfer.files).filter((f) =>
      f.name.toLowerCase().endsWith(".txt")
    );
    onFilesChange(dropped.slice(0, 3));
  };

  return (
    <div className="card">
      <h2>Policy Documents</h2>
      <div className="field">
        <label>
          <input
            type="checkbox"
            checked={useDefaults}
            onChange={(e) => onUseDefaultsChange(e.target.checked)}
          />
          Use bundled synthetic plans (plan_a.txt, plan_b.txt)
        </label>
      </div>
      {!useDefaults && (
        <>
          <label
            className="dropzone"
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            <input
              type="file"
              accept=".txt"
              multiple
              onChange={(e) =>
                onFilesChange(Array.from(e.target.files || []).slice(0, 3))
              }
            />
            Drop .txt policy files here or click to browse
            <br />
            <small>Max 3 files, 500KB each · synthetic/public data only</small>
          </label>
          {files.length > 0 && (
            <ul className="file-list">
              {files.map((f) => (
                <li key={f.name}>{f.name} ({Math.round(f.size / 1024)} KB)</li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

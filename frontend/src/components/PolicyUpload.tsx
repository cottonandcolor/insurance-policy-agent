export type PolicyPreset = "synthetic" | "public_ho3" | "public_flood" | "upload";

interface Props {
  files: File[];
  policyPreset: PolicyPreset;
  onFilesChange: (files: File[]) => void;
  onPolicyPresetChange: (preset: PolicyPreset) => void;
}

const API_BASE = "";

const PRESET_LABELS: Record<Exclude<PolicyPreset, "upload">, string> = {
  synthetic: "Bundled demo (plan_a + plan_b)",
  public_ho3: "Public HO-3 (Travelers NV + State Farm OK)",
  public_flood: "Public flood pair (Travelers HO-3 + FEMA NFIP)",
};

export function PolicyUpload({
  files,
  policyPreset,
  onFilesChange,
  onPolicyPresetChange,
}: Props) {
  const isUpload = policyPreset === "upload";

  const selectPreset = (preset: Exclude<PolicyPreset, "upload">) => {
    onPolicyPresetChange(preset);
    onFilesChange([]);
  };

  const selectUpload = () => {
    onPolicyPresetChange("upload");
  };

  const addFiles = (incoming: File[]) => {
    const txt = incoming.filter((f) => f.name.toLowerCase().endsWith(".txt"));
    if (txt.length === 0) return;
    onPolicyPresetChange("upload");
    onFilesChange(txt.slice(0, 3));
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    addFiles(Array.from(e.dataTransfer.files));
  };

  return (
    <div className="card">
      <h2>Policy Documents</h2>
      <p className="help-text">
        Compare bundled synthetic plans, <strong>real public specimen forms</strong> from state
        regulators and FEMA, or upload your own <strong>.txt</strong> files.
      </p>

      <div className="source-toggle" role="radiogroup" aria-label="Policy source">
        {(Object.keys(PRESET_LABELS) as Array<Exclude<PolicyPreset, "upload">>).map((preset) => (
          <label
            key={preset}
            className={policyPreset === preset ? "source-option active" : "source-option"}
          >
            <input
              type="radio"
              name="policy-source"
              checked={policyPreset === preset}
              onChange={() => selectPreset(preset)}
            />
            {PRESET_LABELS[preset]}
          </label>
        ))}
        <label className={isUpload ? "source-option active" : "source-option"}>
          <input
            type="radio"
            name="policy-source"
            checked={isUpload}
            onChange={selectUpload}
          />
          Upload my policies
        </label>
      </div>

      <label
        className={`dropzone ${!isUpload ? "dropzone-muted" : ""}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
      >
        <input
          type="file"
          accept=".txt,text/plain"
          multiple
          disabled={!isUpload}
          onChange={(e) => addFiles(Array.from(e.target.files || []))}
        />
        {!isUpload ? (
          <>
            Select <strong>Upload my policies</strong> above, or drop files here to switch
          </>
        ) : (
          <>
            Drop .txt files here or click to browse
            <br />
            <small>1–3 files · max 500KB each · Section headers recommended</small>
          </>
        )}
      </label>

      {!isUpload && (
        <p className="help-text">
          Public specimens are sourced from{" "}
          <a href="https://docs.nv.gov/doi/" target="_blank" rel="noreferrer">
            Nevada DOI
          </a>
          ,{" "}
          <a href="https://www.oid.ok.gov/" target="_blank" rel="noreferrer">
            Oklahoma OID
          </a>
          , and{" "}
          <a href="https://www.fema.gov/flood-insurance" target="_blank" rel="noreferrer">
            FEMA NFIP
          </a>
          . See <code>data/public/SOURCES.md</code> in the repo.
        </p>
      )}

      {isUpload && (
        <div className="upload-actions">
          <a
            className="btn-secondary"
            href={`${API_BASE}/api/samples/plan_a.txt`}
            download="plan_a_sample.txt"
          >
            Sample format
          </a>
          <a
            className="btn-secondary"
            href={`${API_BASE}/api/samples/travelers_ho3_nv.txt`}
            download="travelers_ho3_nv.txt"
          >
            Travelers HO-3
          </a>
          <a
            className="btn-secondary"
            href={`${API_BASE}/api/samples/fema_nfip_dwelling_2021.txt`}
            download="fema_nfip_dwelling_2021.txt"
          >
            FEMA NFIP
          </a>
          {files.length > 0 && (
            <button type="button" className="btn-secondary" onClick={() => onFilesChange([])}>
              Clear files
            </button>
          )}
        </div>
      )}

      {files.length > 0 && (
        <ul className="file-list">
          {files.map((f) => (
            <li key={f.name}>
              {f.name} ({Math.round(f.size / 1024)} KB)
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

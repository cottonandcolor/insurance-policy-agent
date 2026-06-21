import type { ProfileInput } from "../api";

interface Props {
  profile: ProfileInput;
  onChange: (profile: ProfileInput) => void;
}

export function ProfileForm({ profile, onChange }: Props) {
  const set = (key: keyof ProfileInput, value: string | number | boolean) => {
    onChange({ ...profile, [key]: value });
  };

  return (
    <div className="card">
      <h2>Your Profile</h2>
      <div className="field">
        <label htmlFor="age">Age</label>
        <input
          id="age"
          type="number"
          min={18}
          max={99}
          value={profile.age}
          onChange={(e) => set("age", Number(e.target.value))}
        />
      </div>
      <div className="field">
        <label htmlFor="location">Location</label>
        <input
          id="location"
          type="text"
          value={profile.location}
          onChange={(e) => set("location", e.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="home_value">Home value ($)</label>
        <input
          id="home_value"
          type="number"
          min={50000}
          step={10000}
          value={profile.home_value}
          onChange={(e) => set("home_value", Number(e.target.value))}
        />
      </div>
      <div className="field">
        <label>
          <input
            type="checkbox"
            checked={profile.flood_zone}
            onChange={(e) => set("flood_zone", e.target.checked)}
          />
          I live in a flood zone
        </label>
      </div>
      <div className="field">
        <label>Priority weights (should sum to ~1.0)</label>
        <div className="weights">
          <div>
            <label htmlFor="cov">Coverage</label>
            <input
              id="cov"
              type="number"
              min={0}
              max={1}
              step={0.1}
              value={profile.coverage_breadth}
              onChange={(e) => set("coverage_breadth", Number(e.target.value))}
            />
          </div>
          <div>
            <label htmlFor="cost">Low cost</label>
            <input
              id="cost"
              type="number"
              min={0}
              max={1}
              step={0.1}
              value={profile.low_cost}
              onChange={(e) => set("low_cost", Number(e.target.value))}
            />
          </div>
          <div>
            <label htmlFor="excl">Few exclusions</label>
            <input
              id="excl"
              type="number"
              min={0}
              max={1}
              step={0.1}
              value={profile.few_exclusions}
              onChange={(e) => set("few_exclusions", Number(e.target.value))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

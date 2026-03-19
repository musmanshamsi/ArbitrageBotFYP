import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Save, Eye, EyeOff, ShieldCheck } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Settings = () => {
  const { toast } = useToast();
  const [showBinanceKey, setShowBinanceKey] = useState(false);
  const [showBybitKey, setShowBybitKey] = useState(false);

  const [settings, setSettings] = useState({
    binanceApiKey: "",
    binanceSecret: "",
    bybitApiKey: "",
    bybitSecret: "",
    maxRiskLoss: 2,
    minSpreadThreshold: 0.3,
  });

  const handleSave = () => {
    toast({
      title: "Settings saved successfully",
      description: "Your configuration has been updated. The bot will use these settings on next start.",
    });
  };

  return (
    <div className="max-w-2xl space-y-8 p-6">
      <div>
        <h2 className="text-xl font-bold text-foreground">Configuration</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Manage your exchange API keys and risk parameters.
        </p>
      </div>

      {/* Binance API */}
      <div className="rounded-lg border border-border bg-card p-6 space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-warning" />
          <h3 className="font-semibold text-foreground">Binance API</h3>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">API Key</label>
            <div className="relative">
              <input
                type={showBinanceKey ? "text" : "password"}
                value={settings.binanceApiKey}
                onChange={(e) => setSettings({ ...settings, binanceApiKey: e.target.value })}
                placeholder="Enter your Binance API key"
                className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
              />
              <button
                onClick={() => setShowBinanceKey(!showBinanceKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showBinanceKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Secret Key</label>
            <input
              type="password"
              value={settings.binanceSecret}
              onChange={(e) => setSettings({ ...settings, binanceSecret: e.target.value })}
              placeholder="Enter your Binance Secret key"
              className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
          </div>
        </div>
      </div>

      {/* Bybit API */}
      <div className="rounded-lg border border-border bg-card p-6 space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-warning" />
          <h3 className="font-semibold text-foreground">Bybit API</h3>
        </div>
        <div className="space-y-3">
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">API Key</label>
            <div className="relative">
              <input
                type={showBybitKey ? "text" : "password"}
                value={settings.bybitApiKey}
                onChange={(e) => setSettings({ ...settings, bybitApiKey: e.target.value })}
                placeholder="Enter your Bybit API key"
                className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
              />
              <button
                onClick={() => setShowBybitKey(!showBybitKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showBybitKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Secret Key</label>
            <input
              type="password"
              value={settings.bybitSecret}
              onChange={(e) => setSettings({ ...settings, bybitSecret: e.target.value })}
              placeholder="Enter your Bybit Secret key"
              className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
          </div>
        </div>
      </div>

      {/* Risk Parameters */}
      <div className="rounded-lg border border-border bg-card p-6 space-y-4">
        <h3 className="font-semibold text-foreground">Risk Management</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Max Risk Loss (%)</label>
            <input
              type="number"
              step="0.1"
              min="0"
              max="100"
              value={settings.maxRiskLoss}
              onChange={(e) => setSettings({ ...settings, maxRiskLoss: parseFloat(e.target.value) })}
              className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground mb-1 block">Min Spread Threshold (%)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="10"
              value={settings.minSpreadThreshold}
              onChange={(e) => setSettings({ ...settings, minSpreadThreshold: parseFloat(e.target.value) })}
              className="w-full rounded-md border border-border bg-secondary/50 px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
          </div>
        </div>
      </div>

      <Button variant="success" size="lg" className="h-12 px-8" onClick={handleSave}>
        <Save className="mr-2 h-4 w-4" />
        Save Settings
      </Button>
    </div>
  );
};

export default Settings;

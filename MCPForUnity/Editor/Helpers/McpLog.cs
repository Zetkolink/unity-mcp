using MCPForUnity.Editor.Constants;
using UnityEditor;
using UnityEngine;

namespace MCPForUnity.Editor.Helpers
{
    internal enum McpLogLevel
    {
        Error = 0,
        Warning = 1,
        Info = 2,
        Debug = 3
    }

    internal static class McpLog
    {
        private const string InfoPrefix = "<b><color=#2EA3FF>MCP-FOR-UNITY</color></b>:";
        private const string DebugPrefix = "<b><color=#6AA84F>MCP-FOR-UNITY</color></b>:";
        private const string WarnPrefix = "<b><color=#cc7a00>MCP-FOR-UNITY</color></b>:";
        private const string ErrorPrefix = "<b><color=#cc3333>MCP-FOR-UNITY</color></b>:";

        private static volatile McpLogLevel _currentLevel = ReadLogLevelPreference();

        public static McpLogLevel GetLogLevel() => _currentLevel;

        public static void SetLogLevel(McpLogLevel level)
        {
            _currentLevel = level;
            try { EditorPrefs.SetInt(EditorPrefKeys.LogLevel, (int)level); }
            catch { }
        }

        public static void SetDebugLoggingEnabled(bool enabled)
        {
            SetLogLevel(enabled ? McpLogLevel.Debug : McpLogLevel.Info);
        }

        public static void Debug(string message)
        {
            if (_currentLevel < McpLogLevel.Debug) return;
            UnityEngine.Debug.Log($"{DebugPrefix} {message}");
        }

        public static void Info(string message, bool always = true)
        {
            if (!always && _currentLevel < McpLogLevel.Debug) return;
            if (always && _currentLevel < McpLogLevel.Info) return;
            UnityEngine.Debug.Log($"{InfoPrefix} {message}");
        }

        public static void Warn(string message)
        {
            if (_currentLevel < McpLogLevel.Warning) return;
            UnityEngine.Debug.LogWarning($"{WarnPrefix} {message}");
        }

        public static void Error(string message)
        {
            UnityEngine.Debug.LogError($"{ErrorPrefix} {message}");
        }

        private static McpLogLevel ReadLogLevelPreference()
        {
            try
            {
                if (EditorPrefs.HasKey(EditorPrefKeys.LogLevel))
                    return (McpLogLevel)EditorPrefs.GetInt(EditorPrefKeys.LogLevel, (int)McpLogLevel.Info);

                // Backward compat: migrate from old boolean DebugLogs pref
                if (EditorPrefs.GetBool(EditorPrefKeys.DebugLogs, false))
                    return McpLogLevel.Debug;

                return McpLogLevel.Info;
            }
            catch { return McpLogLevel.Info; }
        }
    }
}

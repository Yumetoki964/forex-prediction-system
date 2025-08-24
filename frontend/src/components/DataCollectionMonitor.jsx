import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  Database,
  TrendingUp,
  Calendar,
  Activity
} from "lucide-react";
import axios from 'axios';
import { format } from 'date-fns';

const DataCollectionMonitor = () => {
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [dataGaps, setDataGaps] = useState([]);
  const [updateStats, setUpdateStats] = useState(null);
  const [dataIntegrity, setDataIntegrity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeJobs, setActiveJobs] = useState([]);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8174';

  // スケジューラーステータスを取得
  const fetchSchedulerStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/scheduler/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSchedulerStatus(response.data);
      setActiveJobs(response.data.jobs || []);
    } catch (error) {
      console.error('Failed to fetch scheduler status:', error);
    }
  };

  // データギャップを取得
  const fetchDataGaps = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/data-update/gaps`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDataGaps(response.data);
    } catch (error) {
      console.error('Failed to fetch data gaps:', error);
    }
  };

  // 更新統計を取得
  const fetchUpdateStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/data-update/statistics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUpdateStats(response.data);
    } catch (error) {
      console.error('Failed to fetch update statistics:', error);
    }
  };

  // データ整合性を取得
  const fetchDataIntegrity = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/data-update/integrity`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDataIntegrity(response.data);
    } catch (error) {
      console.error('Failed to fetch data integrity:', error);
    }
  };

  // 初期データ取得
  useEffect(() => {
    fetchSchedulerStatus();
    fetchDataGaps();
    fetchUpdateStats();
    fetchDataIntegrity();

    // 30秒ごとに更新
    const interval = setInterval(() => {
      fetchSchedulerStatus();
      fetchUpdateStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // スケジューラーを開始/停止
  const toggleScheduler = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const endpoint = schedulerStatus?.scheduler_running 
        ? '/api/scheduler/stop' 
        : '/api/scheduler/start';
      
      await axios.post(`${API_BASE}${endpoint}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchSchedulerStatus();
    } catch (error) {
      console.error('Failed to toggle scheduler:', error);
    } finally {
      setLoading(false);
    }
  };

  // ジョブを手動実行
  const triggerJob = async (jobId) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_BASE}/api/scheduler/jobs/${jobId}/trigger`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchSchedulerStatus();
    } catch (error) {
      console.error('Failed to trigger job:', error);
    } finally {
      setLoading(false);
    }
  };

  // データギャップを埋める
  const fillDataGaps = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_BASE}/api/data-update/gaps/fill`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchDataGaps();
      await fetchUpdateStats();
    } catch (error) {
      console.error('Failed to fill data gaps:', error);
    } finally {
      setLoading(false);
    }
  };

  // 最新データを更新
  const updateLatestData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(`${API_BASE}/api/data-update/latest`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchUpdateStats();
    } catch (error) {
      console.error('Failed to update latest data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* スケジューラーステータス */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              スケジューラー管理
            </span>
            <div className="flex items-center gap-2">
              <Badge variant={schedulerStatus?.scheduler_running ? "success" : "secondary"}>
                {schedulerStatus?.scheduler_running ? "稼働中" : "停止中"}
              </Badge>
              <Button
                onClick={toggleScheduler}
                disabled={loading}
                size="sm"
                variant={schedulerStatus?.scheduler_running ? "destructive" : "default"}
              >
                {schedulerStatus?.scheduler_running ? (
                  <><Pause className="h-4 w-4 mr-1" /> 停止</>
                ) : (
                  <><Play className="h-4 w-4 mr-1" /> 開始</>
                )}
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {activeJobs.map(job => (
              <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{job.name}</p>
                  <p className="text-sm text-gray-600">
                    次回実行: {job.next_run ? format(new Date(job.next_run), 'yyyy/MM/dd HH:mm') : 'N/A'}
                  </p>
                </div>
                <Button
                  onClick={() => triggerJob(job.id)}
                  disabled={loading}
                  size="sm"
                  variant="outline"
                >
                  <RefreshCw className="h-4 w-4 mr-1" />
                  手動実行
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* データ収集統計 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              データ収集統計
            </CardTitle>
          </CardHeader>
          <CardContent>
            {updateStats && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">総レコード数</span>
                  <span className="font-bold">{updateStats.total_records?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">ユニーク日数</span>
                  <span className="font-bold">{updateStats.unique_days}</span>
                </div>
                {updateStats.sources && Object.entries(updateStats.sources).map(([source, data]) => (
                  <div key={source} className="pt-2 border-t">
                    <p className="font-medium mb-1">{source}</p>
                    <div className="text-sm text-gray-600">
                      <p>レコード数: {data.records_count}</p>
                      {data.update_times?.last && (
                        <p>最終更新: {format(new Date(data.update_times.last), 'MM/dd HH:mm')}</p>
                      )}
                    </div>
                  </div>
                ))}
                <Button
                  onClick={updateLatestData}
                  disabled={loading}
                  className="w-full mt-4"
                  variant="outline"
                >
                  <TrendingUp className="h-4 w-4 mr-2" />
                  最新データを取得
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              データ整合性
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dataIntegrity && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">整合性スコア</span>
                  <div className="flex items-center gap-2">
                    <Progress value={dataIntegrity.integrity_score} className="w-24" />
                    <span className="font-bold">{dataIntegrity.integrity_score}%</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">チェック済みレコード</span>
                  <span className="font-bold">{dataIntegrity.records_checked}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">検出された問題</span>
                  <Badge variant={dataIntegrity.issues_found > 0 ? "destructive" : "success"}>
                    {dataIntegrity.issues_found}
                  </Badge>
                </div>
                {dataIntegrity.issues_found > 0 && (
                  <div className="mt-3 p-3 bg-red-50 rounded">
                    <p className="text-sm font-medium text-red-800 mb-2">検出された問題:</p>
                    {dataIntegrity.issues.slice(0, 3).map((issue, idx) => (
                      <p key={idx} className="text-xs text-red-600">
                        {issue.date}: {issue.type}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* データギャップ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              データギャップ検出
            </span>
            {dataGaps.length > 0 && (
              <Button
                onClick={fillDataGaps}
                disabled={loading}
                size="sm"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                ギャップを埋める
              </Button>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {dataGaps.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>データギャップは検出されませんでした</p>
            </div>
          ) : (
            <div className="space-y-3">
              {dataGaps.map((gap, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-yellow-50 rounded">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                    <div>
                      <p className="font-medium">
                        {gap.start_date} 〜 {gap.end_date}
                      </p>
                      <p className="text-sm text-gray-600">
                        {gap.days}日分のデータが欠損
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DataCollectionMonitor;
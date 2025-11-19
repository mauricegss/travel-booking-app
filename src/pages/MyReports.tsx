import { useEffect, useState } from "react";
import { getReports, deleteReport, TripDataResponse } from "@/services/api";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Trash2, Eye } from "lucide-react";

const MyReports = () => {
  const [reports, setReports] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchReports = async () => {
    try {
        const data = await getReports();
        setReports(data);
    } catch (e) {
        console.error(e);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDelete = async (id: number) => {
    await deleteReport(id);
    fetchReports(); // Recarrega a lista
  };

  const handleView = (report: any) => {
    // Reconstrói o objeto esperado pela SearchResults
    const apiResponse: TripDataResponse = {
        final_report: report.content,
        destination: report.destination,
        start_date: report.start_date,
        end_date: report.end_date,
        error: null
    };
    navigate("/search-results", { state: { apiResponse } });
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Meus Relatórios Salvos</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {reports.map((report) => (
          <Card key={report.id}>
            <CardHeader>
              <CardTitle>{report.destination}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{report.start_date} até {report.end_date}</p>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={() => handleView(report)}>
                    <Eye className="w-4 h-4 mr-2" /> Ver
                </Button>
                <Button variant="destructive" onClick={() => handleDelete(report.id)}>
                    <Trash2 className="w-4 h-4" />
                </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};
export default MyReports;
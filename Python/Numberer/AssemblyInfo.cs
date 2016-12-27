using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using Rhino.PlugIns;

[assembly: PlugInDescription(DescriptionType.Address,      "3670 Woodland Park Ave.N.\nSeattle, WA\n98103")]
[assembly: PlugInDescription(DescriptionType.Country,      "USA")]
[assembly: PlugInDescription(DescriptionType.Email,        "pascal@mcneel.com")]
[assembly: PlugInDescription(DescriptionType.Phone,        "")]
[assembly: PlugInDescription(DescriptionType.Organization, "Pascal")]
[assembly: PlugInDescription(DescriptionType.UpdateUrl,    "")]
[assembly: PlugInDescription(DescriptionType.WebSite,      "")]

[assembly: AssemblyTitle("Numberer")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("Numberer")]
[assembly: AssemblyCopyright("Copyright © Pascal 2015")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]

[assembly: ComVisible(false)]
[assembly: Guid("575fbd89-6445-8541-945b-1839b24a1edf")]
[assembly: AssemblyVersion("1.0.*")]
[assembly: AssemblyFileVersion("1.0.0.0")]
[assembly: AssemblyInformationalVersion("2")]

public class CompilerPlugin : PlugIn 
{ 
  protected override LoadReturnCode OnLoad(ref string errorMessage)
  {
    // Display message.
    string message = @"Loading Numberer.rhp";
    if (!string.IsNullOrEmpty(message))
      Rhino.RhinoApp.WriteLine(message);

    return LoadReturnCode.Success;
  }

  private static bool librariesLoaded = false;
  internal static void LoadLibraries()
  {
    if (librariesLoaded) return;
    librariesLoaded = true;

    
  }
}
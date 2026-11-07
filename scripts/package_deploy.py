"""Build a whitelist-only deployment ZIP, without confidential original scripts."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
FILES = ['app.py','run_pipeline.py','requirements.txt','README.md','DEPLOYMENT.md',
         'SOLUTION_DOC.md','SOLUTION_DOC.html','.gitignore','.streamlit/config.toml',
         'scripts/package_deploy.py']
FILES += [str(p.relative_to(ROOT)) for folder in ('src','tests') for p in sorted((ROOT/folder).glob('*.py'))]
FILES += ['raw_outputs/'+name for name in ('all_episodes_promos_ranked.json',
          'top_promos_ranked.csv','top_promos_report.md','quality_and_failure_audit.md','manifest.json')]

def main():
    target=ROOT/'streamlit_deploy.zip'
    with ZipFile(target,'w',ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(ROOT/name,name)
    with ZipFile(target) as archive:
        assert set(archive.namelist())==set(FILES)
        assert all('secrets.toml' not in name and not name.endswith('.txt') or name=='requirements.txt' for name in archive.namelist())
        assert 'app.py' in archive.namelist()
    print(f'{target.name}: {len(FILES)} files; {target.stat().st_size:,} bytes. No original screenplay files, input archives, or API secrets included.')

if __name__=='__main__': main()
